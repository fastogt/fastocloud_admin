from flask_classy import FlaskView, route
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user

from pyfastocloud_models.service.entry import ServiceSettings
import pyfastocloud_models.constants as constants


# routes
class ProviderView(FlaskView):
    route_base = '/'

    @login_required
    def dashboard(self):
        server = current_user.get_current_server()
        if server:
            streams = server.get_streams()
            streams_relay_encoder_timeshifts = []
            vods = []
            cods = []
            proxy = []
            catchups = []
            events = []
            tests = []
            for stream in streams:
                front = stream.to_dict()
                type = stream.get_type()
                if type == constants.StreamType.PROXY or type == constants.StreamType.VOD_PROXY:
                    proxy.append(front)
                elif type == constants.StreamType.VOD_RELAY or type == constants.StreamType.VOD_ENCODE:
                    vods.append(front)
                elif type == constants.StreamType.COD_RELAY or type == constants.StreamType.COD_ENCODE:
                    cods.append(front)
                elif type == constants.StreamType.CATCHUP:
                    catchups.append(front)
                elif type == constants.StreamType.EVENT:
                    events.append(front)
                elif type == constants.StreamType.TEST_LIFE:
                    tests.append(front)
                else:
                    streams_relay_encoder_timeshifts.append(front)

            role = server.get_user_role_by_id(current_user.id)
            return render_template('provider/dashboard.html', streams=streams_relay_encoder_timeshifts, vods=vods,
                                   cods=cods, proxies=proxy, catchups=catchups, events=events, tests=tests,
                                   service=server, servers=current_user.servers, role=role)

        return redirect(url_for('ProviderView:settings'))

    @route('/settings', methods=['GET'])
    @login_required
    def settings(self):
        return render_template('provider/settings.html', servers=current_user.servers)

    @login_required
    def change_current_server(self, position):
        if position.isdigit():
            current_user.set_current_server_position(int(position))
        return self.dashboard()

    @login_required
    def logout(self):
        current_user.logout()
        return redirect(url_for('HomeView:index'))

    @login_required
    def remove(self):
        servers = ServiceSettings.objects.all()
        for server in servers:
            server.remove_provider(current_user)

        current_user.delete()
        return redirect(url_for('HomeView:index'))
