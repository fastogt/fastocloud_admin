import os

from flask_classy import FlaskView, route
from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user

from app import get_runtime_folder
from app.service.forms import ServiceSettingsForm, ActivateForm, UploadM3uForm, UserServerForm
from app.service.service_entry import ServiceSettings, UserPair
from app.utils.m3u_parser import M3uParser
from app.home.user_loging_manager import User
import app.constants as constants


# routes
class ServiceView(FlaskView):
    route_base = "/service/"

    @login_required
    @route('/upload_m3u', methods=['POST', 'GET'])
    def upload_m3u(self):
        form = UploadM3uForm()
        return render_template('service/upload_m3u.html', form=form)

    @login_required
    @route('/upload_file', methods=['POST'])
    def upload_file(self):
        form = UploadM3uForm()
        server = current_user.get_current_server()
        if server and form.validate_on_submit():
            stream_type = form.type.data
            file_handle = form.file.data
            m3u_parser = M3uParser()
            m3u_parser.load_content(file_handle.read().decode('utf-8'))
            m3u_parser.parse()

            for file in m3u_parser.files:
                if stream_type == constants.StreamType.RELAY:
                    stream = server.make_relay_stream()
                    stream.output.urls[0] = stream.generate_http_link()
                elif stream_type == constants.StreamType.ENCODE:
                    stream = server.make_encode_strema()
                    stream.output.urls[0] = stream.generate_http_link()
                elif stream_type == constants.StreamType.VOD_RELAY:
                    stream = server.make_vod_relay_stream()
                    stream.output.urls[0] = stream.generate_vod_link()
                elif stream_type == constants.StreamType.VOD_ENCODE:
                    stream = server.make_vod_encode_stream()
                    stream.output.urls[0] = stream.generate_vod_link()
                elif stream_type == constants.StreamType.CATCHUP:
                    stream = server.make_catchup_stream()
                    stream.output.urls[0] = stream.generate_http_link()
                else:
                    stream = server.make_test_life_stream()

                stream.input.urls[0].uri = file['link']
                stream.name = file['title'] if file['title'] else constants.DEFAULT_STREAM_NAME
                stream.group = file['tvg-group'] if file['tvg-group'] else constants.DEFAULT_STREAM_GROUP_TITLE
                server.add_stream(stream)

        return redirect(url_for('UserView:dashboard'))

    @login_required
    def connect(self):
        server = current_user.get_current_server()
        if server:
            server.connect()
        return redirect(url_for('UserView:dashboard'))

    @login_required
    def disconnect(self):
        server = current_user.get_current_server()
        if server:
            server.disconnect()
        return redirect(url_for('UserView:dashboard'))

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
                    return redirect(url_for('UserView:dashboard'))

        return render_template('service/activate.html', form=form)

    @login_required
    def sync(self):
        server = current_user.get_current_server()
        if server:
            server.sync()
        return redirect(url_for('UserView:dashboard'))

    @login_required
    def stop(self):
        server = current_user.get_current_server()
        if server:
            server.stop(1)
        return redirect(url_for('UserView:dashboard'))

    @login_required
    def ping(self):
        server = current_user.get_current_server()
        if server:
            server.ping()
        return redirect(url_for('UserView:dashboard'))

    @login_required
    def get_log(self):
        server = current_user.get_current_server()
        if server:
            server.get_log_service()
        return redirect(url_for('UserView:dashboard'))

    @login_required
    def view_playlist(self):
        server = current_user.get_current_server()
        if server:
            return '<pre>{0}</pre>'.format(server.view_playlist())
        return '''<pre>Not found, please create server firstly.</pre>'''

    def playlist(self, sid):
        server = ServiceSettings.objects(id=sid).first()
        if server:
            return server.generate_playlist(), 200

        return jsonify(status='failed'), 404

    @login_required
    def view_log(self):
        server = current_user.get_current_server()
        if server:
            path = os.path.join(get_runtime_folder(), server.id)
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
    @route('/user/add/<sid>', methods=['GET', 'POST'])
    def user_add(self, sid):
        form = UserServerForm()
        if request.method == 'POST' and form.validate_on_submit():
            user = User.objects(email=form.email.data).first()
            server = ServiceSettings.objects(id=sid).first()
            if server and user:
                admin = UserPair(user.id, form.role.data)
                server.add_user(admin)
                user.add_server(server)
                return jsonify(status='ok'), 200

        return render_template('service/user/add.html', form=form)

    @login_required
    @route('/add', methods=['GET', 'POST'])
    def add(self):
        model = ServiceSettings()
        form = ServiceSettingsForm(obj=model)
        if request.method == 'POST' and form.validate_on_submit():
            new_entry = form.make_entry()
            admin = UserPair(current_user.id, constants.Roles.ADMIN)
            new_entry.add_user(admin)
            current_user.add_server(new_entry)
            return jsonify(status='ok'), 200

        return render_template('service/add.html', form=form)

    @login_required
    @route('/remove', methods=['POST'])
    def remove(self):
        sid = request.form['sid']
        server = ServiceSettings.objects(id=sid).first()
        if server:
            current_user.remove_server(server)
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
