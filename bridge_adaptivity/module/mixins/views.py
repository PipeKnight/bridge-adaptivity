import logging

from django import forms
from django.core.cache import cache
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect

from module.forms import BaseGradingPolicyForm, GroupForm
from module.models import Collection, CollectionGroup, Course, Engine, GRADING_POLICY_NAME_TO_CLS

log = logging.getLogger(__name__)


class CollectionIdToContextMixin(object):
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(CollectionIdToContextMixin, self).get_context_data(**kwargs)
        context['current_collection_id'] = self.kwargs.get('collection_id')
        return context

    def form_valid(self, form):
        try:
            return super(CollectionIdToContextMixin, self).form_valid(form)
        except (ValidationError, TypeError):
            return redirect("{}?engine=failure".format(self.get_success_url()))


class LtiSessionMixin(object):

    def dispatch(self, request, *args, **kwargs):
        lti_session = request.session.get('Lti_session')
        sequence_id = request.session.get('Lti_sequence')
        if not lti_session:
            log.error('Lti session is not found, Request cannot be processed')
            raise PermissionDenied("Course content is available only through LTI protocol.")
        elif lti_session != cache.get(sequence_id):
            cache.set(sequence_id, lti_session)
            if request.session['Lti_strict_forward']:
                request.session['Lti_update_activity'] = True
                log.debug("[StrictForward] Session is changed, activity update could be required: {}".format(
                    request.session['Lti_update_activity'])
                )
        return super(LtiSessionMixin, self).dispatch(request, *args, **kwargs)


class GroupEditFormMixin(object):
    form_class = GroupForm
    prefix = 'group'
    grading_prefix = 'grading'

    def get_grading_form_kwargs(self):
        """Return kwargs for GradingForm."""
        form_kw = dict(
            prefix=self.grading_prefix,
        )
        if self.object and self.object.grading_policy:
            form_kw['instance'] = self.object.grading_policy
        return form_kw

    def form_valid(self, form):
        POST = self.request.POST.copy()
        form_kw = self.get_grading_form_kwargs()
        policy = GRADING_POLICY_NAME_TO_CLS[POST['group-grading_policy_name']]
        GradingPolicyForm = policy.get_form_class()

        grading_policy_form = GradingPolicyForm(self.request.POST, **form_kw)
        if grading_policy_form.is_valid():
            response = super(GroupEditFormMixin, self).form_valid(form)
            grading_policy = grading_policy_form.save()
            self.object.grading_policy = grading_policy
            self.object.save()
        else:
            return self.form_invalid(form)
        return response

    def get_context_data(self, **kwargs):
        data = super(GroupEditFormMixin, self).get_context_data(**kwargs)
        form_kw = self.get_grading_form_kwargs()
        post_or_none = self.request.POST if self.request.POST else None
        data['grading_policy_form'] = BaseGradingPolicyForm(post_or_none, **form_kw)
        return data

    def get_form(self):
        form = super(GroupEditFormMixin, self).get_form()
        collections = Collection.objects.filter(
            owner=self.request.user
        )
        form.fields['engine'].initial = Engine.get_default()
        form.fields['course'].queryset = Course.objects.filter(owner=self.request.user)
        form.fields['collections'].queryset = collections
        if self.kwargs.get('group_slug'):
            group = get_object_or_404(CollectionGroup, slug=self.kwargs['group_slug'])
            if group.grading_policy:
                form.fields['grading_policy_name'].initial = group.grading_policy.name
        return form


class OnlyMyObjectsMixin(object):
    owner_field = 'owner'

    def get_queryset(self):
        qs = super(OnlyMyObjectsMixin, self).get_queryset()
        return qs.filter(**{self.owner_field: self.request.user})


class BackURLMixin(object):
    def get_context_data(self, **kwargs):
        context = super(BackURLMixin, self).get_context_data(**kwargs)
        back_url = self.request.GET.get('back_url')
        if back_url:
            context['back_url'] = back_url
        return context


class SetUserInFormMixin(object):
    owner_field_name = 'owner'

    def get_form(self):
        form = super(SetUserInFormMixin, self).get_form()
        if form.fields.get(self.owner_field_name):
            form.fields['owner'].initial = self.request.user
            form.fields['owner'].widget = forms.HiddenInput(attrs={'readonly': True})
        return form