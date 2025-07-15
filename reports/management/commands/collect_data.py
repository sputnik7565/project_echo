import json
import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from reports.models import Brand, Report
from reports.services.youtube_collector import YouTubeCollector
from reports.services.naver_collector import NaverCollector
from reports.services.gemini_analyzer import GeminiAnalyzer
from reports.services.chart_service import ChartService
from django.core.cache import cache
from django.conf import settings

def _json_to_markdown(report_json):
    md_content = []

    # Report Meta
    if "report_meta" in report_json:
        md_content.append(f"# {report_json['report_meta'].get('title', '리포트')}")
        md_content.append(f"\n**기간:** {report_json['report_meta'].get('period', 'N/A')}\n")

    # Weekly Headline
    if "weekly_headline" in report_json:
        md_content.append(f"## 주간 헤드라인\n> {report_json['weekly_headline']}\n")

    # Executive Summary
    if "executive_summary" in report_json:
        md_content.append(f"## {report_json['executive_summary'].get('title', '핵심 요약')}\n")
        for point in report_json['executive_summary'].get('summary_points', []):
            md_content.append(f"- {point.get('point', '')}")
            if point.get("data_source"):
                md_content.append(f"  (출처: {point['data_source']})\n")
        md_content.append("\n")

    # Performance Dashboard
    if "performance_dashboard" in report_json:
        md_content.append(f"## {report_json['performance_dashboard'].get('title', '성과 대시보드')}\n")
        for metric in report_json['performance_dashboard'].get('metrics', []):
            md_content.append(f"### {metric.get('metric_name', '')}\n")
            md_content.append(f"- **값:** {metric.get('value', 'N/A')}\n")
            md_content.append(f"- **인사이트:** {metric.get('insight', 'N/A')}\n")
            if metric.get("data_source"): 
                md_content.append(f"- **출처:** {metric['data_source']}\n")
        md_content.append("\n")

    # Deep Dive
    if "deep_dive" in report_json:
        md_content.append(f"## {report_json['deep_dive'].get('title', '상세 분석')}\n")
        for section in report_json['deep_dive'].get('sections', []):
            md_content.append(f"### {section.get('section_title', '')}\n")
            md_content.append(f"- **발견:** {section.get('finding', '')}\n")
            if section.get("evidence"): 
                md_content.append(f"- **근거:**\n  ```\n  {section['evidence']}\n  ```\n")
            md_content.append(f"- **제안:** {section.get('recommendation', '')}\n")
            if section.get("data_source"): 
                md_content.append(f"- **출처:** {section['data_source']}\n")
        md_content.append("\n")

    # Strategic Recommendations
    if "strategic_recommendations" in report_json:
        md_content.append(f"## {report_json['strategic_recommendations'].get('title', '전략적 제언')}\n")
        for rec in report_json['strategic_recommendations'].get('recommendations', []):
            md_content.append(f"### {rec.get('priority', '')}: {rec.get('action', '')}\n")
            md_content.append(f"- **근거:** {rec.get('rationale', '')}\n")
            md_content.append(f"- **기대 효과:** {rec.get('expected_impact', '')}\n")
        md_content.append("\n")

    return "\n".join(md_content)

class Command(BaseCommand):
    help = 'Collects marketing data, analyzes it with Gemini, generates charts, and saves a structured report.'

    def add_arguments(self, parser):
        parser.add_argument('--client_brand', type=str, required=True, help='The brand name of the client.')
        parser.add_argument('--competitor_brand', type=str, required=True, help='The name of the main competitor brand.')
        parser.add_argument('--target_persona_keywords', type=str, required=True, help='Comma-separated keywords describing the target audience.')
        parser.add_argument('--task_id', type=str, help='Unique ID for the task progress tracking.')

    def _update_progress(self, task_id, stage, status, message=""):
        if task_id:
            cache.set(task_id, {'stage': stage, 'status': status, 'message': message}, timeout=300) # Cache for 5 minutes

    def handle(self, *args, **options):
        task_id = options.get('task_id')
        self._update_progress(task_id, "start", "in_progress", "리포트 생성 프로세스 시작...")
        self.stdout.write(self.style.SUCCESS('Starting the report generation process...'))
        
        client_brand_name = options['client_brand']
        competitor_brand_name = options['competitor_brand']
        target_persona_keywords = options['target_persona_keywords']

        # -- 1. Setup --
        youtube_collector = YouTubeCollector()
        naver_collector = NaverCollector()
        gemini_analyzer = GeminiAnalyzer()
        chart_service = ChartService(client_brand_name)

        client_brand, _ = Brand.objects.get_or_create(name=client_brand_name, defaults={'brand_type': 'main'})

        self.stdout.write(self.style.NOTICE(f'Processing: Client=[{client_brand_name}], Competitor=[{competitor_brand_name}]'))
        
        # -- 2. Data Collection --
        self._update_progress(task_id, "data_collection", "in_progress", "데이터 수집 중...")
        self.stdout.write(self.style.NOTICE('Phase 1: Collecting data...'))
        raw_data = {'youtube': {}, 'naver': {}}
        try:
            # YouTube Data
            client_channel_details = youtube_collector.get_channel_details_by_name(client_brand_name)
            competitor_channel_details = youtube_collector.get_channel_details_by_name(competitor_brand_name)
            raw_data['youtube']['client'] = {'channel_details': client_channel_details}
            raw_data['youtube']['competitor'] = {'channel_details': competitor_channel_details}
            # Naver Data
            end_date = timezone.now().strftime('%Y-%m-%d')
            start_date = (timezone.now() - timezone.timedelta(days=30)).strftime('%Y-%m-%d')
            raw_data['naver']['search_trends'] = naver_collector.get_search_trends(keywords=[[client_brand_name], [competitor_brand_name]], start_date=start_date, end_date=end_date)
            raw_data['naver']['shopping_results'] = {
                'client': naver_collector.search_shopping(client_brand_name),
                'competitor': naver_collector.search_shopping(competitor_brand_name)
            }
            self.stdout.write(self.style.SUCCESS('-> Data collection complete.'))
            self._update_progress(task_id, "data_collection", "completed", "데이터 수집 완료.")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Data collection failed: {e}'))
            self._update_progress(task_id, "data_collection", "failed", f"데이터 수집 실패: {e}")
            return

        # -- 3. Chart Generation --
        self._update_progress(task_id, "chart_generation", "in_progress", "차트 생성 중...")
        self.stdout.write(self.style.NOTICE('Phase 2: Generating charts...'))
        generated_chart_paths = {}
        try:
            # Naver Search Trend Chart
            generated_chart_paths['naver_search_trend'] = chart_service.generate_naver_search_trend_chart(
                raw_data['naver']['search_trends'][client_brand_name],
                raw_data['naver']['search_trends'][competitor_brand_name],
                client_brand_name, competitor_brand_name
            )
            # YouTube Subscriber Chart
            generated_chart_paths['youtube_subscriber'] = chart_service.generate_youtube_subscriber_chart(
                raw_data['youtube']['client']['channel_details']['statistics'],
                raw_data['youtube']['competitor']['channel_details']['statistics'],
                client_brand_name, competitor_brand_name
            )
            # YouTube View Chart
            generated_chart_paths['youtube_view'] = chart_service.generate_youtube_view_chart(
                raw_data['youtube']['client']['channel_details']['statistics'],
                raw_data['youtube']['competitor']['channel_details']['statistics'],
                client_brand_name, competitor_brand_name
            )
            # Shopping SOV Chart
            client_reviews = sum(item.get('reviewCount', 0) for item in raw_data['naver']['shopping_results']['client'].get('items', []))
            competitor_reviews = sum(item.get('reviewCount', 0) for item in raw_data['naver']['shopping_results']['competitor'].get('items', []))
            generated_chart_paths['shopping_sov'] = chart_service.generate_shopping_sov_chart(
                client_reviews, competitor_reviews, client_brand_name, competitor_brand_name
            )
            self.stdout.write(self.style.SUCCESS('-> Chart generation complete.'))
            self._update_progress(task_id, "chart_generation", "completed", "차트 생성 완료.")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Chart generation failed: {e}'))
            self._update_progress(task_id, "chart_generation", "failed", f"차트 생성 실패: {e}")
            # Continue without charts if generation fails

        # -- 4. AI Analysis --
        self._update_progress(task_id, "ai_analysis", "in_progress", "AI 분석 중...")
        self.stdout.write(self.style.NOTICE('Phase 3: Analyzing data with Gemini AI...'))
        report_data = gemini_analyzer.analyze_data(raw_data, client_brand_name, competitor_brand_name, target_persona_keywords)
        if 'error' in report_data:
            self.stdout.write(self.style.ERROR(f"Gemini analysis failed: {report_data['error']}"))
            self._update_progress(task_id, "ai_analysis", "failed", f"AI 분석 실패: {report_data['error']}")
            return
        self.stdout.write(self.style.SUCCESS('-> Gemini AI analysis successful.'))
        self._update_progress(task_id, "ai_analysis", "completed", "AI 분석 완료.")

        # -- 5. Save Report --
        self._update_progress(task_id, "save_report", "in_progress", "리포트 저장 중...")
        self.stdout.write(self.style.NOTICE('Phase 4: Saving the report...'))
        try:
            Report.objects.create(
                brand=client_brand,
                report_date=timezone.now().date(),
                competitor_brand_name=competitor_brand_name,
                raw_data=raw_data,
                report_data=report_data,
                generated_chart_paths=generated_chart_paths
            )
            self.stdout.write(self.style.SUCCESS(f'-> Report for {client_brand_name} saved successfully!'))
            self._update_progress(task_id, "save_report", "completed", "리포트 저장 완료.")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to save report: {e}'))
            self._update_progress(task_id, "save_report", "failed", f"리포트 저장 실패: {e}")

        # -- 6. Save Report as Markdown --
        self._update_progress(task_id, "save_markdown", "in_progress", "마크다운 리포트 저장 중...")
        markdown_output = _json_to_markdown(report_data)
        output_dir = os.path.join(settings.BASE_DIR, 'report_data') # Changed folder name
        os.makedirs(output_dir, exist_ok=True)
        
        report_filename = f"{client_brand_name}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.md"
        output_filepath = os.path.join(output_dir, report_filename)
        
        try:
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_output)
            self.stdout.write(self.style.SUCCESS(f'-> Report saved as Markdown: {output_filepath}'))
            self._update_progress(task_id, "save_markdown", "completed", "마크다운 리포트 저장 완료.")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to save Markdown report: {e}'))
            self._update_progress(task_id, "save_markdown", "failed", f"마크다운 리포트 저장 실패: {e}")

        self.stdout.write(self.style.SUCCESS('Report generation process finished.'))
        self._update_progress(task_id, "finished", "completed", "리포트 생성 프로세스 완료.")