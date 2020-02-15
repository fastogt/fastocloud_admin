from flask_classy import FlaskView, route
from flask import request, jsonify, render_template, redirect, url_for
from flask_login import login_required

from pyfastocloud_models.utils.m3u_parser import M3uParser
from app.common.service.forms import UploadM3uForm
import pyfastocloud_models.constants as constants
from app.autofill.entry import M3uParseStreams, M3uParseVods
from pyfastocloud_models.utils.utils import is_valid_http_url


# routes
class M3uParseStreamsView(FlaskView):
    route_base = '/m3uparse_streams/'

    @login_required
    def show(self):
        m3u = M3uParseStreams.objects()
        return render_template('autofill/show_streams.html', m3u=m3u)

    def show_anonim(self):
        m3u = M3uParseStreams.objects()
        return render_template('autofill/show_streams_anonim.html', m3u=m3u)

    @route('/search/<sid>', methods=['GET'])
    def search(self, sid):
        lines = M3uParseStreams.objects(id=sid)
        line = lines.first()
        if line:
            return jsonify(status='ok', line=line), 200

        return jsonify(status='failed', error='Not found'), 404

    @route('/upload_files', methods=['POST'])
    @login_required
    def upload_files(self):
        form = UploadM3uForm()
        if form.validate_on_submit():
            files = request.files.getlist("files")
            for file in files:
                m3u_parser = M3uParser()
                data = file.read().decode('utf-8')
                m3u_parser.load_content(data)
                m3u_parser.parse()

                for file in m3u_parser.files:
                    title = file['title']
                    if len(title) > constants.MAX_STREAM_NAME_LENGTH:
                        continue

                    line = M3uParseStreams.objects(name=title).first()
                    if not line:
                        line = M3uParseStreams(name=title)

                    tvg_id = file['tvg-id']
                    if len(tvg_id) and len(tvg_id) < constants.MAX_STREAM_TVG_ID_LENGTH:
                        line.tvg_id.append(tvg_id)

                    tvg_group = file['tvg-group']
                    if len(tvg_group) and len(tvg_group) < constants.MAX_STREAM_GROUP_TITLE_LENGTH:
                        line.group.append(tvg_group)

                    tvg_logo = file['tvg-logo']
                    if len(tvg_logo) and len(tvg_logo) < constants.MAX_URL_LENGTH:
                        if is_valid_http_url(tvg_logo, timeout=0.1):
                            line.tvg_logo.append(tvg_logo)

                    line.save()

        return redirect(url_for('M3uParseStreamsView:show'))

    @login_required
    @route('/upload_m3u', methods=['POST', 'GET'])
    def upload_m3u(self):
        form = UploadM3uForm()
        return render_template('autofill/upload_m3u_streams.html', form=form)


# routes
class M3uParseVodsView(FlaskView):
    route_base = '/m3uparse_vods/'

    @login_required
    def show(self):
        m3u = M3uParseVods.objects()
        return render_template('autofill/show_vods.html', m3u=m3u)

    @login_required
    def show_anonim(self):
        m3u = M3uParseVods.objects()
        return render_template('autofill/show_vods_anonim.html', m3u=m3u)

    @route('/search/<sid>', methods=['GET'])
    def search(self, sid):
        lines = M3uParseVods.objects(id=sid)
        line = lines.first()
        if line:
            return jsonify(status='ok', line=line), 200

        return jsonify(status='failed', error='Not found'), 404

    @route('/upload_files', methods=['POST'])
    @login_required
    def upload_files(self):
        form = UploadM3uForm()
        if form.validate_on_submit():
            files = request.files.getlist("files")
            for file in files:
                m3u_parser = M3uParser()
                data = file.read().decode('utf-8')
                m3u_parser.load_content(data)
                m3u_parser.parse()

                for file in m3u_parser.files:
                    title = file['title']
                    if len(title) > constants.MAX_STREAM_NAME_LENGTH:
                        continue

                    line = M3uParseVods.objects(name=title).first()
                    if not line:
                        line = M3uParseVods(name=title)

                    tvg_group = file['tvg-group']
                    if len(tvg_group) and len(tvg_group) < constants.MAX_STREAM_GROUP_TITLE_LENGTH:
                        line.group.append(tvg_group)

                    tvg_logo = file['tvg-logo']
                    if len(tvg_logo) and len(tvg_logo) < constants.MAX_URL_LENGTH:
                        if is_valid_http_url(tvg_logo, timeout=0.1):
                            line.tvg_logo.append(tvg_logo)

                    line.save()

        return redirect(url_for('M3uParseVodsView:show'))

    @login_required
    @route('/upload_m3u', methods=['POST', 'GET'])
    def upload_m3u(self):
        form = UploadM3uForm()
        return render_template('autofill/upload_m3u_vods.html', form=form)
