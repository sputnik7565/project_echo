from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from weasyprint import HTML
from .models import Report
from django.core.management import call_command
from django.contrib import messages
from io import StringIO
import uuid
from django.core.cache import cache
import threading
from .management.commands.collect_data import _json_to_markdown # Import the markdown conversion function
from django.conf import settings # Import settings

def hub_page(request):
    reports = Report.objects.all().order_by('-report_date')
    return render(request, 'reports/hub_page.html', {'reports': reports})

def _run_collect_data_command(client_brand, competitor_brand, target_persona_keywords, task_id):
    try:
        call_command('collect_data', 
                     client_brand=client_brand, 
                     competitor_brand=competitor_brand, 
                     target_persona_keywords=target_persona_keywords,
                     task_id=task_id)
    except Exception as e:
        # Log the error internally if needed
        print(f"Error running collect_data command for task {task_id}: {e}")
        cache.set(task_id, {'stage': 'error', 'status': 'failed', 'message': f"리포트 생성 중 치명적인 오류 발생: {e}"}, timeout=300)

def generate_report_view(request):
    if request.method == 'POST':
        client_brand = request.POST.get('client_brand')
        competitor_brand = request.POST.get('competitor_brand')
        target_persona_keywords = request.POST.get('target_persona_keywords')

        if not all([client_brand, competitor_brand, target_persona_keywords]):
            return JsonResponse({'status': 'error', 'message': "모든 필드를 입력해주세요."}, status=400)

        task_id = str(uuid.uuid4())
        
        # Run the management command in a separate thread
        thread = threading.Thread(target=_run_collect_data_command, args=(client_brand, competitor_brand, target_persona_keywords, task_id))
        thread.start()

        return JsonResponse({'status': 'success', 'task_id': task_id, 'message': "리포트 생성이 시작되었습니다."}) # No redirect
    else:
        return redirect('reports:hub_page')

def get_report_progress(request):
    task_id = request.GET.get('task_id')
    if not task_id:
        return JsonResponse({'status': 'error', 'message': 'task_id가 필요합니다.'}, status=400)

    progress = cache.get(task_id)
    if progress is None:
        return JsonResponse({'status': 'error', 'message': '진행 상황을 찾을 수 없습니다. 태스크가 만료되었거나 존재하지 않습니다.'}, status=404)
    
    return JsonResponse(progress)

def delete_report(request, report_id):
    if request.method == 'POST':
        report = get_object_or_404(Report, pk=report_id)
        report.delete()
        messages.success(request, "리포트가 성공적으로 삭제되었습니다.")
        return JsonResponse({'status': 'success', 'message': '리포트가 삭제되었습니다.'})
    return JsonResponse({'status': 'error', 'message': '잘못된 요청 방식입니다.'}, status=400)

def download_markdown_report(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    markdown_content = _json_to_markdown(report.report_data)
    
    response = HttpResponse(markdown_content, content_type='text/markdown; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{report.brand.name}_{report.report_date.strftime("%Y%m%d")}.md"'
    return response

def report_list(request):
    reports = Report.objects.all().order_by('-report_date')
    return render(request, 'reports/report_list.html', {'reports': reports})

def report_detail(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    context = {
        'report': report,
        'data': report.report_data or {}  # Pass report_data under the key 'data'
    }
    return render(request, 'reports/report_detail.html', context)

def report_pdf(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    template = get_template('reports/report_detail.html')
    context = {
        'report': report,
        'data': report.report_data or {}
    }
    html = template.render(context)
    
    # Pass base_url to HTML to correctly resolve static and media files
    try:
        pdf_file = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="report_{report.brand.name}_{report.report_date.strftime("%Y%m%d")}.pdf"'
        return response
    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error generating PDF: {e}")
        return HttpResponse(f"PDF 생성 중 오류가 발생했습니다: {e}", status=500)