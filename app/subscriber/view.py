from flask_classy import FlaskView, route
from flask import render_template, request, jsonify
from flask_login import login_required
from bson.objectid import ObjectId

from app.common.subscriber.forms import SignupForm
from pyfastocloud_models.subscriber.login.entry import SubscriberUser
from pyfastocloud_models.service.entry import ServiceSettings


def _get_subscriber_by_id(sid: str):
    try:
        subscriber = SubscriberUser.objects.get({'_id': ObjectId(sid)})
    except SubscriberUser.DoesNotExist:
        return None
    else:
        return subscriber


# routes
class SubscriberView(FlaskView):
    route_base = "/subscriber/"

    @login_required
    def show(self):
        return render_template('subscriber/show.html', subscribers=SubscriberUser.objects.all())

    @login_required
    @route('/add', methods=['GET', 'POST'])
    def add(self):
        form = SignupForm()
        if request.method == 'POST' and form.validate_on_submit():
            new_entry = form.make_entry()
            servers = ServiceSettings.objects.all()
            for server in servers:
                new_entry.add_server(server)
            new_entry.save()
            return jsonify(status='ok'), 200

        return render_template('subscriber/add.html', form=form)

    @login_required
    @route('/edit/<sid>', methods=['GET', 'POST'])
    def edit(self, sid):
        subscriber = _get_subscriber_by_id(sid)
        form = SignupForm(obj=subscriber)
        if request.method == 'POST' and form.validate_on_submit():
            subscriber = form.update_entry(subscriber)
            subscriber.save()
            return jsonify(status='ok'), 200

        return render_template('subscriber/edit.html', form=form)

    @login_required
    @route('/remove', methods=['POST'])
    def remove(self):
        data = request.get_json()
        sid = data['sid']
        subscriber = _get_subscriber_by_id(sid)
        if subscriber:
            subscriber.delete()
            return jsonify(status='ok'), 200

        return jsonify(status='failed'), 404
