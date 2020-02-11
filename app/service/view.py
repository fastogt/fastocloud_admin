import os

from flask_classy import FlaskView, route
from flask import render_template, redirect, url_for, request, jsonify, Response
from flask_login import login_required, current_user

from app import get_runtime_folder
from app.common.service.forms import ServiceSettingsForm, ActivateForm, UploadM3uForm, ServerProviderForm
from pyfastocloud_models.service.entry import ServiceSettings, ProviderPair
from pyfastocloud_models.utils.m3u_parser import M3uParser
from pyfastocloud_models.utils.utils import is_valid_http_url
from app.home.entry import ProviderAdminUser
import pyfastocloud_models.constants as constants


# routes
class ServiceView(FlaskView):
    route_base = "/service/"

    def default_logo_url(self):
        return url_for('static', filename='images/unknown_channel.png', _external=True)

    @login_required
    @route('/upload_m3u', methods=['POST', 'GET'])
    def upload_m3u(self):
        form = UploadM3uForm()
        return render_template('service/upload_m3u.html', form=form)

    @login_required
    @route('/upload_files', methods=['POST'])
    def upload_files(self):
        form = UploadM3uForm()
        server = current_user.get_current_server()
        if server and form.validate_on_submit():
            stream_type = form.type.data
            files = request.files.getlist("files")
            for file in files:
                m3u_parser = M3uParser()
                data = file.read().decode('utf-8')
                m3u_parser.load_content(data)
                m3u_parser.parse()

                streams = []
                default_logo_path = self.default_logo_url()
                for file in m3u_parser.files:
                    if stream_type == constants.StreamType.PROXY:
                        stream = server.make_proxy_stream()
                    elif stream_type == constants.StreamType.VOD_PROXY:
                        stream = server.make_proxy_vod()
                    elif stream_type == constants.StreamType.RELAY:
                        stream = server.make_relay_stream()
                        stream.output.urls[0] = stream.generate_http_link(constants.HlsType.HLS_PULL,
                                                                          oid=stream.output.urls[0].id)
                    elif stream_type == constants.StreamType.ENCODE:
                        stream = server.make_encode_stream()
                        stream.output.urls[0] = stream.generate_http_link(constants.HlsType.HLS_PULL,
                                                                          oid=stream.output.urls[0].id)
                    elif stream_type == constants.StreamType.VOD_RELAY:
                        stream = server.make_vod_relay_stream()
                        stream.output.urls[0] = stream.generate_vod_link(constants.HlsType.HLS_PULL,
                                                                         oid=stream.output.urls[0].id)
                    elif stream_type == constants.StreamType.VOD_ENCODE:
                        stream = server.make_vod_encode_stream()
                        stream.output.urls[0] = stream.generate_vod_link(constants.HlsType.HLS_PULL,
                                                                         oid=stream.output.urls[0].id)
                    elif stream_type == constants.StreamType.COD_RELAY:
                        stream = server.make_cod_relay_stream()
                        stream.output.urls[0] = stream.generate_cod_link(constants.HlsType.HLS_PULL,
                                                                         oid=stream.output.urls[0].id)
                    elif stream_type == constants.StreamType.COD_ENCODE:
                        stream = server.make_cod_encode_stream()
                        stream.output.urls[0] = stream.generate_cod_link(constants.HlsType.HLS_PULL,
                                                                         oid=stream.output.urls[0].id)
                    elif stream_type == constants.StreamType.CATCHUP:
                        stream = server.make_catchup_stream()
                    else:
                        stream = server.make_test_life_stream()

                    input_url = file['link']
                    if stream_type == constants.StreamType.PROXY or stream_type == constants.StreamType.VOD_PROXY:
                        stream.output.urls[0].uri = input_url
                    else:
                        stream.input.urls[0].uri = input_url

                    stream.tvg_logo = default_logo_path

                    title = file['title']
                    if len(title) < constants.MAX_STREAM_NAME_LENGTH:
                        stream.name = title

                    tvg_id = file['tvg-id']
                    if len(tvg_id) < constants.MAX_STREAM_TVG_ID_LENGTH:
                        stream.tvg_id = tvg_id

                    tvg_name = file['tvg-name']
                    if len(tvg_name) < constants.MAX_STREAM_NAME_LENGTH:
                        stream.tvg_name = tvg_name

                    tvg_group = file['tvg-group']
                    if len(tvg_group) < constants.MAX_STREAM_GROUP_TITLE_LENGTH:
                        stream.group = tvg_group

                    tvg_logo = file['tvg-logo']
                    if len(tvg_logo) < constants.MAX_URL_LENGTH:
                        if is_valid_http_url(tvg_logo, timeout=0.1):
                            stream.tvg_logo = tvg_logo

                    stream.save()
                    streams.append(stream)

                server.add_streams(streams)

        return redirect(url_for('ProviderView:dashboard'))

    @login_required
    def connect(self):
        server = current_user.get_current_server()
        if server:
            server.connect()
        return redirect(url_for('ProviderView:dashboard'))

    @login_required
    def disconnect(self):
        server = current_user.get_current_server()
        if server:
            server.disconnect()
        return redirect(url_for('ProviderView:dashboard'))

    @route('/activate', methods=['POST', 'GET'])
    @login_required
    def activate(self):
        form = ActivateForm()
        if request.method == 'POST':
            server = current_user.get_current_server()
            if server:
                if form.validate_on_submit():
                    license = form.license.data
                    server.activate(license)
                    return redirect(url_for('ProviderView:dashboard'))

        return render_template('service/activate.html', form=form)

    @login_required
    def sync(self):
        server = current_user.get_current_server()
        if server:
            server.sync()
        return redirect(url_for('ProviderView:dashboard'))

    @login_required
    def stop(self):
        server = current_user.get_current_server()
        if server:
            server.stop(1)
        return redirect(url_for('ProviderView:dashboard'))

    @login_required
    def ping(self):
        server = current_user.get_current_server()
        if server:
            server.ping()
        return redirect(url_for('ProviderView:dashboard'))

    @login_required
    def get_log(self):
        server = current_user.get_current_server()
        if server:
            server.get_log_service()
        return redirect(url_for('ProviderView:dashboard'))

    @login_required
    @route('/playlist/<sid>/master.m3u', methods=['GET'])
    def playlist(self, sid):
        server = ServiceSettings.objects(id=sid).first()
        if server:
            return Response(server.generate_playlist(), mimetype='application/x-mpequrl'), 200

        return jsonify(status='failed'), 404

    @login_required
    def view_log(self):
        server = current_user.get_current_server()
        if server:
            path = os.path.join(get_runtime_folder(), str(server.id))
            try:
                with open(path, "r") as f:
                    content = f.read()

                return content
            except OSError as e:
                print('Caught exception OSError : {0}'.format(e))
                return '''<pre>Not found, please use get log button firstly.</pre>'''
        return '''<pre>Not found, please create server firstly.</pre>'''

    # broadcast routes

    @login_required
    def providers(self, sid):
        server = ServiceSettings.objects(id=sid).first()
        if server:
            return render_template('service/providers.html', server=server)

        return redirect(url_for('ProviderView:dashboard'))

    @login_required
    @route('/provider/add/<sid>', methods=['GET', 'POST'])
    def provider_add(self, sid):
        form = ServerProviderForm()
        if request.method == 'POST' and form.validate_on_submit():
            email = form.email.data.lower()
            provider = ProviderAdminUser.objects(email=email).first()
            server = ServiceSettings.objects(id=sid).first()
            if server and provider:
                admin = ProviderPair(provider.id, form.role.data)
                server.add_provider(admin)
                provider.add_server(server)
                return jsonify(status='ok'), 200

        return render_template('service/provider/add.html', form=form)

    @login_required
    @route('/provider/remove/<sid>', methods=['POST'])
    def provider_remove(self, sid):
        data = request.get_json()
        pid = data['pid']
        provider = ProviderAdminUser.objects(id=pid).first()
        server = ServiceSettings.objects(id=sid).first()
        if provider and server:
            server.remove_provider(provider)
            provider.remove_server(server)
            return jsonify(status='ok'), 200

        return jsonify(status='failed'), 404

    @login_required
    @route('/add', methods=['GET', 'POST'])
    def add(self):
        form = ServiceSettingsForm(obj=ServiceSettings())
        if request.method == 'POST' and form.validate_on_submit():
            new_entry = form.make_entry()
            admin = ProviderPair(user=current_user.id, role=ProviderPair.Roles.ADMIN)
            new_entry.add_provider(admin)
            current_user.add_server(new_entry)
            return jsonify(status='ok'), 200

        return render_template('service/add.html', form=form)

    @login_required
    @route('/remove', methods=['POST'])
    def remove(self):
        sid = request.form['sid']
        server = ServiceSettings.objects(id=sid).first()
        if server:
            server.delete()
            return jsonify(status='ok'), 200

        return jsonify(status='failed'), 404

    @login_required
    @route('/edit/<sid>', methods=['GET', 'POST'])
    def edit(self, sid):
        server = ServiceSettings.objects(id=sid).first()
        form = ServiceSettingsForm(obj=server)

        if request.method == 'POST' and form.validate_on_submit():
            server = form.update_entry(server)
            server.save()
            return jsonify(status='ok'), 200

        return render_template('service/edit.html', form=form)

    @route('/log/<sid>', methods=['POST'])
    def log(self, sid):
        # len = request.headers['content-length']
        new_file_path = os.path.join(get_runtime_folder(), sid)
        with open(new_file_path, 'wb') as f:
            data = request.stream.read()
            f.write(b'<pre>')
            f.write(data)
            f.write(b'</pre>')
            f.close()
        return jsonify(status='ok'), 200
