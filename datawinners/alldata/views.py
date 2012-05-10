import base64
import urllib2
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from datawinners.accountmanagement.views import is_new_user
from datawinners.alldata.helper import get_all_project_for_user, get_visibility_settings_for, get_page_heading,get_reports_list
from datawinners.local_settings import CRS_ORG_ID
from datawinners.main.utils import get_database_manager
from datawinners.project.models import ProjectState, Project
from datawinners.project.views import project_overview, project_data, project_results, web_questionnaire
from mangrove.form_model.form_model import FormModel
from datawinners.submission.models import DatawinnerLog
from datawinners.utils import get_organization
from datawinners.entity.views import create_subject
from datawinners.accountmanagement.views import is_not_expired

def get_crs_project_links():
    project_links = {'projects_link': reverse(index),
                     'reports_link': reverse(reports),
                     }
    return project_links


def projects_index(request):
    reporter_id = request.user.get_profile().reporter_id
    manager = get_database_manager(request.user)
    project_list = []
    rows = get_all_project_for_user(request.user)
    disable_link_class, hide_link_class = get_visibility_settings_for(request.user)
    page_heading = get_page_heading(request.user)
    for row in rows:
        analysis = log = "#"
        disabled = "disable_link"
        project_id = row['value']['_id']
        project = Project.load(manager.database, project_id)
        questionnaire = manager.get(project['qid'], FormModel)
        questionnaire_code = questionnaire.form_code
        link = reverse(project_overview, args=[project_id])
        web_submission_link = reverse(web_questionnaire, args=[project_id])
        if project.state != ProjectState.INACTIVE:
            disabled = ""
            analysis = reverse(project_data, args=[project_id, questionnaire_code])
            log = reverse(project_results, args=[project_id, questionnaire_code])

        web_submission_link_disabled = 'disable_link'
        if 'web' in row['value']['devices']:
            web_submission_link_disabled = ""
        create_subjects_link = ''
        if 'no' in row['value']['activity_report']:
            create_subjects_link = reverse(create_subject, args=[project.entity_type])
        project_info = dict(name=row['value']['name'], created=row['value']['created'],
            type=row['value']['project_type'],
            link=link, log=log, analysis=analysis, disabled=disabled, web_submission_link=web_submission_link,
            web_submission_link_disabled=web_submission_link_disabled, create_subjects_link=create_subjects_link,
            entity_type=project.entity_type)
        project_list.append(project_info)
    return disable_link_class, hide_link_class, page_heading, project_list


@login_required(login_url='/login')
@is_new_user
@is_not_expired
def index(request):
    disable_link_class, hide_link_class, page_heading, project_list = projects_index(request)
    organization_id = get_organization(request).org_id
    if organization_id == CRS_ORG_ID:
        return render_to_response('alldata/index.html',
            {'projects': project_list, 'page_heading': page_heading, 'disable_link_class': disable_link_class,
             'hide_link_class': hide_link_class, 'is_crs_user' : True, 'project_links' : get_crs_project_links()},
            context_instance=RequestContext(request))
    else:
        return render_to_response('alldata/index.html',
                {'projects': project_list, 'page_heading': page_heading, 'disable_link_class': disable_link_class,
                 'hide_link_class': hide_link_class, 'is_crs_user' : False},
                context_instance=RequestContext(request))



@login_required(login_url='/login')
@is_not_expired
def failed_submissions(request):
    logs = DatawinnerLog.objects.all()
    organization = get_organization(request)
    org_logs = [log for log in logs if log.organization == organization]
    return render_to_response('alldata/failed_submissions.html', {'logs': org_logs},
                              context_instance=RequestContext(request))

@login_required(login_url='/login')
@is_not_expired
def reports(request):
    org_id = get_organization(request).org_id
    if org_id != CRS_ORG_ID:
        return HttpResponseRedirect('/alldata/')
    else:
        report_list = get_reports_list(get_organization(request).org_id)
        url = 'http://localhost:8080/WebViewerExample/frameset?__report=crs/waybill_sent_and_received.rptdesign'
        handle = urllib2.Request(url)
        username = 'datawinners'
        password = 'datawinners'
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        handle.add_header("Authorization", "Basic %s" % base64string)
        result1 = urllib2.urlopen(handle)
        headers_list = result1.headers.dict['set-cookie'].split(';')

        cookie_key,cookie_val = headers_list[0].split('=')

        response = render_to_response('alldata/reports_page.html',
                {'reports': report_list, 'page_heading': "Reports",'project_links' : get_crs_project_links()},
            context_instance=RequestContext(request))
        response.set_cookie(cookie_key,value=cookie_val,path=headers_list[1].split('=')[1])
        response['CRS'] = 'Valid'
        return response


