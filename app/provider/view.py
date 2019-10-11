from flask_classy import FlaskView, route
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user

from app.common.provider.forms import SettingsForm
from app.common.service.entry import ServiceSettings


# routes
class ProviderView(FlaskView):
    route_base = "/"

    @login_required
    def dashboard(self):
        server = current_user.get_current_server()
        if server:
            streams = server.get_streams()
            front_streams = []
            for stream in streams:
                front_streams.append(stream.to_dict())
            role = server.get_user_role_by_id(current_user.id)
            return render_template('provider/dashboard.html', streams=front_streams, service=server,
                                   servers=current_user.servers, role=role)

        return redirect(url_for('ProviderView:settings'))

    @route('/settings', methods=['POST', 'GET'])
    @login_required
    def settings(self):
        servers = current_user.servers
        form = SettingsForm(obj=current_user.settings)

        if request.method == 'POST':
            if form.validate_on_submit():
                form.update_settings(current_user.settings)
                current_user.save()
                return render_template('provider/settings.html', form=form, servers=servers)

        return render_template('provider/settings.html', form=form, servers=servers)

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
        servers = ServiceSettings.objects()
        for server in servers:
            server.remove_provider(current_user)

        current_user.delete()
        return redirect(url_for('HomeView:index'))
