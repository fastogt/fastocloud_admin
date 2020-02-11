import os
import datetime
import re

from flask_classy import FlaskView, route
from flask import render_template, request, jsonify, Response
from flask_login import login_required, current_user

import pyfastocloud_models.constants as constants
from app import get_runtime_stream_folder, omdb
from pyfastocloud_models.stream.entry import IStream
from app.common.stream.forms import ProxyStreamForm, EncodeStreamForm, RelayStreamForm, TimeshiftRecorderStreamForm, \
    CatchupStreamForm, TimeshiftPlayerStreamForm, TestLifeStreamForm, VodEncodeStreamForm, VodRelayStreamForm, \
    ProxyVodStreamForm, CodEncodeStreamForm, CodRelayStreamForm, EventStreamForm
from app.common.series.forms import SerialForm


# routes
class StreamView(FlaskView):
    DEFAULT_PIPELINE_FILENAME_TEMPLATE_1S = '{0}_pipeline.html'

    route_base = '/stream/'

    @staticmethod
    def _get_pipeline_name(sid: str):
        return StreamView.DEFAULT_PIPELINE_FILENAME_TEMPLATE_1S.format(sid)

    @login_required
    @route('/start', methods=['POST'])
    def start(self):
        server = current_user.get_current_server()
        if server:
            data = request.get_json()
            sids = data['sids']
            for sid in sids:
                server.start_stream(sid)
            return jsonify(status='ok'), 200
        return jsonify(status='failed'), 404

    @login_required
    @route('/stop', methods=['POST'])
    def stop(self):
        server = current_user.get_current_server()
        if server:
            data = request.get_json()
            sids = data['sids']
            for sid in sids:
                server.stop_stream(sid)
            return jsonify(status='ok'), 200
        return jsonify(status='failed'), 404

    @login_required
    @route('/restart', methods=['POST'])
    def restart(self):
        server = current_user.get_current_server()
        if server:
            data = request.get_json()
            sids = data['sids']
            for sid in sids:
                server.restart_stream(sid)
            return jsonify(status='ok'), 200
        return jsonify(status='failed'), 404

    @login_required
    @route('/play/<sid>/master.m3u', methods=['GET'])
    def play(self, sid):
        stream = IStream.objects(id=sid).first()
        if stream:
            return Response(stream.generate_playlist(), mimetype='application/x-mpequrl'), 200

        return jsonify(status='failed'), 404

    @login_required
    @route('/get_log', methods=['POST'])
    def get_log(self):
        server = current_user.get_current_server()
        if server:
            sid = request.form['sid']
            server.get_log_stream(sid)
            return jsonify(status='ok'), 200
        return jsonify(status='failed'), 404

    @login_required
    @route('/get_pipeline', methods=['POST'])
    def get_pipeline(self):
        server = current_user.get_current_server()
        if server:
            sid = request.form['sid']
            server.get_pipeline_stream(sid)
            return jsonify(status='ok'), 200
        return jsonify(status='failed'), 404

    @login_required
    def view_log(self, sid):
        path = os.path.join(get_runtime_stream_folder(), sid)
        try:
            with open(path, "r") as f:
                content = f.read()
                return content
        except OSError as e:
            print('Caught exception OSError : {0}'.format(e))
            return '''<pre>Not found, please use get log button firstly.</pre>'''

    @login_required
    def view_pipeline(self, sid):
        path = os.path.join(get_runtime_stream_folder(), StreamView._get_pipeline_name(sid))
        try:
            with open(path, "r") as f:
                content = f.read()
                return content
        except OSError as e:
            print('Caught exception OSError : {0}'.format(e))
            return '''<pre>Not found, please use get pipeline button firstly.</pre>'''

    # broadcast routes

    @login_required
    @route('/add/serial', methods=['GET', 'POST'])
    def add_serial(self):
        server = current_user.get_current_server()
        if server:
            serial = server.make_serial()
            form = SerialForm(obj=serial)
            if request.method == 'POST' and form.validate_on_submit():
                new_entry = form.make_entry()
                new_entry.save()
                server.add_serial(new_entry)
                return jsonify(status='ok'), 200

            return render_template('series/add.html', form=form)
        return jsonify(status='failed'), 404

    @login_required
    @route('/add/proxy_stream', methods=['GET', 'POST'])
    def add_proxy_stream(self):
        server = current_user.get_current_server()
        if server:
            stream = server.make_proxy_stream()
            form = ProxyStreamForm(obj=stream)
            if request.method == 'POST' and form.validate_on_submit():
                new_entry = form.make_entry()
                new_entry.save()
                server.add_stream(new_entry)
                return jsonify(status='ok'), 200

            return render_template('stream/proxy/add.html', form=form)
        return jsonify(status='failed'), 404

    @login_required
    @route('/add/proxy_vod', methods=['GET', 'POST'])
    def add_proxy_vod(self):
        server = current_user.get_current_server()
        if server:
            stream = server.make_proxy_vod()
            form = ProxyVodStreamForm(obj=stream)
            if request.method == 'POST' and form.validate_on_submit():
                new_entry = form.make_entry()
                new_entry.save()
                server.add_stream(new_entry)
                return jsonify(status='ok'), 200

            return render_template('stream/vod_proxy/add.html', form=form)
        return jsonify(status='failed'), 404

    @login_required
    @route('/add/vod_proxy_omdb/<oid>', methods=['GET', 'POST'])
    def add_vod_proxy_omdb(self, oid):
        server = current_user.get_current_server()
        if server:
            stream = server.make_proxy_vod()
            form = ProxyVodStreamForm(obj=stream)
            if request.method == 'GET':
                res = omdb.imdbid(oid)
                form.name.data = res['title']
                form.tvg_logo.data = res['poster']
                if res['type'] == 'series':
                    form.vod_type.data = constants.VodType.SERIES
                form.country.data = res['country']
                form.description.data = res['plot']
                form.user_score.data = float(res['imdb_rating']) * 10
                form.group.data = res['genre'].replace(',', ';')
                form.prime_date.data = datetime.datetime.strptime(res['released'], '%d %b %Y')
                runt_raw = res['runtime']
                minutes = re.findall('\d+', runt_raw)
                if minutes:
                    # runt = datetime.time(minute=int(minutes[0]))
                    # mseconds = (runt.hour * 60000 + runt.minute) * 60000 + runt.second * 1000 + runt.microsecond / 1000
                    form.duration.data = int(minutes[0]) * 60000

            if request.method == 'POST' and form.validate_on_submit():
                new_entry = form.make_entry()
                new_entry.save()
                server.add_stream(new_entry)
                return jsonify(status='ok'), 200

            return render_template('stream/vod_proxy/add.html', form=form)
        return jsonify(status='failed'), 404

    @login_required
    @route('/add/relay', methods=['GET', 'POST'])
    def add_relay(self):
        server = current_user.get_current_server()
        if server:
            stream = server.make_relay_stream()
            form = RelayStreamForm(obj=stream)
            if request.method == 'POST' and form.validate_on_submit():
                new_entry = form.update_entry(stream)
                new_entry.save()
                server.add_stream(new_entry)
                return jsonify(status='ok'), 200

            return render_template('stream/relay/add.html', form=form, feedback_dir=stream.generate_feedback_dir())
        return jsonify(status='failed'), 404

    @login_required
    @route('/add/encode', methods=['GET', 'POST'])
    def add_encode(self):
        server = current_user.get_current_server()
        if server:
            stream = server.make_encode_stream()
            form = EncodeStreamForm(obj=stream)
            if request.method == 'POST' and form.validate_on_submit():
                new_entry = form.update_entry(stream)
                new_entry.save()
                server.add_stream(new_entry)
                return jsonify(status='ok'), 200

            return render_template('stream/encode/add.html', form=form, feedback_dir=stream.generate_feedback_dir())
        return jsonify(status='failed'), 404

    @login_required
    @route('/add/timeshift_recorder', methods=['GET', 'POST'])
    def add_timeshift_recorder(self):
        server = current_user.get_current_server()
        if server:
            stream = server.make_timeshift_recorder_stream()
            form = TimeshiftRecorderStreamForm(obj=stream)
            if request.method == 'POST':  # FIXME form.validate_on_submit()
                new_entry = form.update_entry(stream)
                new_entry.save()
                server.add_stream(new_entry)
                return jsonify(status='ok'), 200

            return render_template('stream/timeshift_recorder/add.html', form=form,
                                   feedback_dir=stream.generate_feedback_dir(),
                                   timeshift_dir=stream.generate_timeshift_dir())
        return jsonify(status='failed'), 404

    @login_required
    @route('/add/test_life', methods=['GET', 'POST'])
    def add_test_life(self):
        server = current_user.get_current_server()
        if server:
            stream = server.make_test_life_stream()
            form = TestLifeStreamForm(obj=stream)
            if request.method == 'POST':  # FIXME form.validate_on_submit()
                new_entry = form.update_entry(stream)
                new_entry.save()
                server.add_stream(new_entry)
                return jsonify(status='ok'), 200

            return render_template('stream/test_life/add.html', form=form, feedback_dir=stream.generate_feedback_dir())
        return jsonify(status='failed'), 404

    @login_required
    @route('/add/catchup', methods=['GET', 'POST'])
    def add_catchup(self):
        server = current_user.get_current_server()
        if server:
            stream = server.make_catchup_stream()
            form = CatchupStreamForm(obj=stream)
            if request.method == 'POST':  # FIXME form.validate_on_submit()
                new_entry = form.update_entry(stream)
                new_entry.save()
                server.add_stream(new_entry)
                return jsonify(status='ok'), 200

            return render_template('stream/catchup/add.html', form=form, feedback_dir=stream.generate_feedback_dir(),
                                   timeshift_dir=stream.generate_timeshift_dir())
        return jsonify(status='failed'), 404

    @login_required
    @route('/add/timeshift_player', methods=['GET', 'POST'])
    def add_timeshift_player(self):
        server = current_user.get_current_server()
        if server:
            stream = server.make_timeshift_player_stream()
            form = TimeshiftPlayerStreamForm(obj=stream)
            if request.method == 'POST' and form.validate_on_submit():
                new_entry = form.update_entry(stream)
                new_entry.save()
                server.add_stream(new_entry)
                return jsonify(status='ok'), 200

            return render_template('stream/timeshift_player/add.html', form=form,
                                   feedback_dir=stream.generate_feedback_dir())
        return jsonify(status='failed'), 404

    @login_required
    @route('/add/vod_relay', methods=['GET', 'POST'])
    def add_vod_relay(self):
        server = current_user.get_current_server()
        if server:
            stream = server.make_vod_relay_stream()
            form = VodRelayStreamForm(obj=stream)
            if request.method == 'POST' and form.validate_on_submit():
                new_entry = form.update_entry(stream)
                new_entry.save()
                server.add_stream(new_entry)
                return jsonify(status='ok'), 200

            return render_template('stream/vod_relay/add.html', form=form,
                                   feedback_dir=stream.generate_feedback_dir())
        return jsonify(status='failed'), 404

    @login_required
    @route('/add/vod_encode', methods=['GET', 'POST'])
    def add_vod_encode(self):
        server = current_user.get_current_server()
        if server:
            stream = server.make_vod_encode_stream()
            form = VodEncodeStreamForm(obj=stream)
            if request.method == 'POST' and form.validate_on_submit():
                new_entry = form.update_entry(stream)
                new_entry.save()
                server.add_stream(new_entry)
                return jsonify(status='ok'), 200

            return render_template('stream/vod_encode/add.html', form=form,
                                   feedback_dir=stream.generate_feedback_dir())
        return jsonify(status='failed'), 404

    @login_required
    @route('/add/event', methods=['GET', 'POST'])
    def add_event(self):
        server = current_user.get_current_server()
        if server:
            stream = server.make_event_stream()
            form = EventStreamForm(obj=stream)
            if request.method == 'POST' and form.validate_on_submit():
                new_entry = form.update_entry(stream)
                new_entry.save()
                server.add_stream(new_entry)
                return jsonify(status='ok'), 200

            return render_template('stream/event/add.html', form=form,
                                   feedback_dir=stream.generate_feedback_dir())
        return jsonify(status='failed'), 404

    @login_required
    @route('/add/cod_relay', methods=['GET', 'POST'])
    def add_cod_relay(self):
        server = current_user.get_current_server()
        if server:
            stream = server.make_cod_relay_stream()
            form = CodRelayStreamForm(obj=stream)
            if request.method == 'POST' and form.validate_on_submit():
                new_entry = form.update_entry(stream)
                new_entry.save()
                server.add_stream(new_entry)
                return jsonify(status='ok'), 200

            return render_template('stream/cod_relay/add.html', form=form,
                                   feedback_dir=stream.generate_feedback_dir())
        return jsonify(status='failed'), 404

    @login_required
    @route('/add/cod_encode', methods=['GET', 'POST'])
    def add_cod_encode(self):
        server = current_user.get_current_server()
        if server:
            stream = server.make_cod_encode_stream()
            form = CodEncodeStreamForm(obj=stream)
            if request.method == 'POST' and form.validate_on_submit():
                new_entry = form.update_entry(stream)
                new_entry.save()
                server.add_stream(new_entry)
                return jsonify(status='ok'), 200

            return render_template('stream/cod_encode/add.html', form=form,
                                   feedback_dir=stream.generate_feedback_dir())
        return jsonify(status='failed'), 404

    @login_required
    @route('/edit/<sid>', methods=['GET', 'POST'])
    def edit(self, sid):
        server = current_user.get_current_server()
        if server:
            stream = server.find_stream_by_id(sid)
            if stream:
                type = stream.get_type()
                if type == constants.StreamType.PROXY:
                    form = ProxyStreamForm(obj=stream)

                    if request.method == 'POST' and form.validate_on_submit():
                        stream = form.update_entry(stream)
                        server.update_stream(stream)
                        return jsonify(status='ok'), 200

                    return render_template('stream/proxy/edit.html', form=form)
                elif type == constants.StreamType.VOD_PROXY:
                    form = ProxyVodStreamForm(obj=stream)

                    if request.method == 'POST' and form.validate_on_submit():
                        stream = form.update_entry(stream)
                        server.update_stream(stream)
                        return jsonify(status='ok'), 200

                    return render_template('stream/vod_proxy/edit.html', form=form)
                elif type == constants.StreamType.RELAY:
                    form = RelayStreamForm(obj=stream)

                    if request.method == 'POST' and form.validate_on_submit():
                        stream = form.update_entry(stream)
                        server.update_stream(stream)
                        return jsonify(status='ok'), 200

                    return render_template('stream/relay/edit.html', form=form,
                                           feedback_dir=stream.generate_feedback_dir())
                elif type == constants.StreamType.ENCODE:
                    form = EncodeStreamForm(obj=stream)

                    if request.method == 'POST' and form.validate_on_submit():
                        stream = form.update_entry(stream)
                        server.update_stream(stream)
                        return jsonify(status='ok'), 200

                    return render_template('stream/encode/edit.html', form=form,
                                           feedback_dir=stream.generate_feedback_dir())
                elif type == constants.StreamType.TIMESHIFT_RECORDER:
                    form = TimeshiftRecorderStreamForm(obj=stream)

                    if request.method == 'POST':  # FIXME form.validate_on_submit()
                        stream = form.update_entry(stream)
                        server.update_stream(stream)
                        return jsonify(status='ok'), 200

                    return render_template('stream/timeshift_recorder/edit.html', form=form,
                                           feedback_dir=stream.generate_feedback_dir(),
                                           timeshift_dir=stream.generate_timeshift_dir())
                elif type == constants.StreamType.CATCHUP:
                    form = CatchupStreamForm(obj=stream)

                    if request.method == 'POST':  # FIXME form.validate_on_submit()
                        stream = form.update_entry(stream)
                        server.update_stream(stream)
                        return jsonify(status='ok'), 200

                    return render_template('stream/catchup/edit.html', form=form,
                                           feedback_dir=stream.generate_feedback_dir(),
                                           timeshift_dir=stream.generate_timeshift_dir())
                elif type == constants.StreamType.TIMESHIFT_PLAYER:
                    form = TimeshiftPlayerStreamForm(obj=stream)

                    if request.method == 'POST' and form.validate_on_submit():
                        stream = form.update_entry(stream)
                        server.update_stream(stream)
                        return jsonify(status='ok'), 200

                    return render_template('stream/timeshift_player/edit.html', form=form,
                                           feedback_dir=stream.generate_feedback_dir())
                elif type == constants.StreamType.TEST_LIFE:
                    form = TestLifeStreamForm(obj=stream)

                    if request.method == 'POST':  # FIXME form.validate_on_submit()
                        stream = form.update_entry(stream)
                        server.update_stream(stream)
                        return jsonify(status='ok'), 200

                    return render_template('stream/test_life/edit.html', form=form,
                                           feedback_dir=stream.generate_feedback_dir())
                elif type == constants.StreamType.VOD_RELAY:
                    form = VodRelayStreamForm(obj=stream)

                    if request.method == 'POST' and form.validate_on_submit():
                        stream = form.update_entry(stream)
                        server.update_stream(stream)
                        return jsonify(status='ok'), 200

                    return render_template('stream/vod_relay/edit.html', form=form,
                                           feedback_dir=stream.generate_feedback_dir())
                elif type == constants.StreamType.VOD_ENCODE:
                    form = VodEncodeStreamForm(obj=stream)

                    if request.method == 'POST' and form.validate_on_submit():
                        stream = form.update_entry(stream)
                        server.update_stream(stream)
                        return jsonify(status='ok'), 200

                    return render_template('stream/vod_encode/edit.html', form=form,
                                           feedback_dir=stream.generate_feedback_dir())
                elif type == constants.StreamType.COD_RELAY:
                    form = CodRelayStreamForm(obj=stream)

                    if request.method == 'POST' and form.validate_on_submit():
                        stream = form.update_entry(stream)
                        server.update_stream(stream)
                        return jsonify(status='ok'), 200

                    return render_template('stream/cod_relay/edit.html', form=form,
                                           feedback_dir=stream.generate_feedback_dir())
                elif type == constants.StreamType.COD_ENCODE:
                    form = CodEncodeStreamForm(obj=stream)

                    if request.method == 'POST' and form.validate_on_submit():
                        stream = form.update_entry(stream)
                        server.update_stream(stream)
                        return jsonify(status='ok'), 200

                    return render_template('stream/cod_encode/edit.html', form=form,
                                           feedback_dir=stream.generate_feedback_dir())
                elif type == constants.StreamType.EVENT:
                    form = EventStreamForm(obj=stream)

                    if request.method == 'POST' and form.validate_on_submit():
                        stream = form.update_entry(stream)
                        server.update_stream(stream)
                        return jsonify(status='ok'), 200

                    return render_template('stream/event/edit.html', form=form,
                                           feedback_dir=stream.generate_feedback_dir())

        return jsonify(status='failed'), 404

    @login_required
    @route('/remove', methods=['POST'])
    def remove(self):
        data = request.get_json()
        sids = data['sids']
        server = current_user.get_current_server()
        if server:
            for sid in sids:
                server.remove_stream(sid)
            return jsonify(status='ok'), 200
        return jsonify(status='failed'), 404

    @login_required
    @route('/remove_all_streams', methods=['GET'])
    def remove_all_streams(self):
        server = current_user.get_current_server()
        if server:
            server.remove_all_streams()
            return jsonify(status='ok'), 200
        return jsonify(status='failed'), 404

    @login_required
    @route('/stop_all_streams', methods=['GET'])
    def stop_all_streams(self):
        server = current_user.get_current_server()
        if server:
            server.stop_all_streams()
            return jsonify(status='ok'), 200
        return jsonify(status='failed'), 404

    @login_required
    @route('/start_all_streams', methods=['GET'])
    def start_all_streams(self):
        server = current_user.get_current_server()
        if server:
            server.start_all_streams()
            return jsonify(status='ok'), 200
        return jsonify(status='failed'), 404

    @route('/log/<sid>', methods=['POST'])
    def log(self, sid):
        # len = request.headers['content-length']
        new_file_path = os.path.join(get_runtime_stream_folder(), sid)
        with open(new_file_path, 'wb') as f:
            data = request.stream.read()
            f.write(b'<pre>')
            f.write(data)
            f.write(b'</pre>')
            f.close()

        return jsonify(status='ok'), 200

    @route('/pipeline/<sid>', methods=['POST'])
    def pipeline(self, sid):
        # len = request.headers['content-length']
        new_file_path = os.path.join(get_runtime_stream_folder(), StreamView._get_pipeline_name(sid))
        with open(new_file_path, 'wb') as f:
            data = request.stream.read()
            f.write(data)
            f.close()

        return jsonify(status='ok'), 200
