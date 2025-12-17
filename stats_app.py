import base64
from io import BytesIO
from pathlib import Path
from PIL import Image

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Image as RLImage
from scipy import stats
from scipy.stats import shapiro

# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Statistics 1 Survey Analysis",
    page_icon="📊",
    layout="wide",
)

# ---------------------------------------------------------
# Language options & translator
# ---------------------------------------------------------
LANG_OPTIONS = {
    "id": {
        "label": "Indonesia",
        "page_title": "Analisis Survei Statistik 1",
        "header_title": "Aplikasi Analisis Survei Statistik 1",
        "header_subtitle": "Mata Kuliah: Statistik 1 | Dosen: Dr. Edwin Setiawan Nugraha",
        "nav_title": "Navigasi",
        "steps_title": "Langkah:",
        "step1": "Unggah Dataset",
        "step2": "Pilih Variabel",
        "step3": "Lihat Hasil",
        "members_title": "Anggota Kelompok",
        "dataset_section_title": "1. Unggah Dataset",
        "upload_label": "Unggah dataset Anda (CSV atau Excel)",
        "dataset_loaded": "Dataset berhasil dimuat! Bentuk: {rows} baris × {cols} kolom",
        "view_raw": "Lihat Dataset Mentah",
        "variable_selection_title": "2. Pemilihan Variabel",
        "independent_label": "Variabel Independen (X)",
        "dependent_label": "Variabel Dependen (Y)",
        "select_x": "Pilih kolom untuk Variabel X (item skala Likert)",
        "select_y": "Pilih kolom untuk Variabel Y (item skala Likert)",
        "select_warning": "Pilih minimal satu kolom untuk Variabel X dan Variabel Y.",
        "composite_success": "Skor komposit dihitung: X_total (n={nx}), Y_total (n={ny})",
        "descriptive_title": "3. Statistik Deskriptif",
        "variable_x_items": "Item Variabel X",
        "variable_y_items": "Item Variabel Y",
        "composite_section": "Skor Komposit (X_total dan Y_total)",
        "visual_title": "4. Visualisasi",
        "hist_x": "Histogram: X_total",
        "hist_y": "Histogram: Y_total",
        "boxplots": "Boxplot",
        "scatter": "Scatter Plot: X_total vs Y_total",
        "association_title": "5. Analisis Hubungan",
        "assumption_checks": "Pemeriksaan Asumsi",
        "normality_x": "Uji Normalitas X_total",
        "normality_y": "Uji Normalitas Y_total",
        "recommendation_title": "Rekomendasi Jenis Korelasi:",
        "corr_choice": "Pilih jenis korelasi yang ingin dihitung:",
        "corr_analysis": "Analisis Korelasi",
        "pdf_title": "6. Ekspor Laporan PDF",
        "download_pdf": "Unduh Laporan PDF",
        "insufficient_data": "Data tidak cukup untuk analisis korelasi. Minimal 3 pasangan valid diperlukan.",
        "upload_info": "👆 Unggah file CSV atau Excel untuk memulai analisis.",
        "unsupported_format": "Format file tidak didukung. Harap unggah file CSV atau Excel.",
        "error_loading": "Gagal memuat dataset. Periksa format file Anda.",
        "reco_pearson": "Gunakan Pearson correlation karena X_total dan Y_total memenuhi asumsi normalitas (p ≥ 0.05).",
        "reco_spearman": "Gunakan Spearman correlation karena setidaknya salah satu variabel tidak normal dan/atau berskala ordinal.",
    },
    "en": {
        "label": "English",
        "page_title": "Statistics 1 Survey Analysis",
        "header_title": "Statistics 1 Survey Analysis Application",
        "header_subtitle": "Course: Statistics 1 | Lecturer: Dr. Edwin Setiawan Nugraha",
        "nav_title": "Navigation",
        "steps_title": "Steps:",
        "step1": "Upload Dataset",
        "step2": "Select Variables",
        "step3": "View Results",
        "members_title": "Group Members",
        "dataset_section_title": "1. Dataset Upload",
        "upload_label": "Upload your dataset (CSV or Excel)",
        "dataset_loaded": "Dataset loaded successfully! Shape: {rows} rows × {cols} columns",
        "view_raw": "View Raw Dataset",
        "variable_selection_title": "2. Variable Selection",
        "independent_label": "Independent Variable (X)",
        "dependent_label": "Dependent Variable (Y)",
        "select_x": "Select columns for Variable X (Likert-scale items)",
        "select_y": "Select columns for Variable Y (Likert-scale items)",
        "select_warning": "Please select at least one column for both Variable X and Variable Y.",
        "composite_success": "Composite scores computed: X_total (n={nx}), Y_total (n={ny})",
        "descriptive_title": "3. Descriptive Statistics",
        "variable_x_items": "Variable X Items",
        "variable_y_items": "Variable Y Items",
        "composite_section": "Composite Scores (X_total and Y_total)",
        "visual_title": "4. Visualizations",
        "hist_x": "Histogram: X_total",
        "hist_y": "Histogram: Y_total",
        "boxplots": "Boxplots",
        "scatter": "Scatter Plot: X_total vs Y_total",
        "association_title": "5. Association Analysis",
        "assumption_checks": "Assumption Checks",
        "normality_x": "X_total Normality Test",
        "normality_y": "Y_total Normality Test",
        "recommendation_title": "Correlation Method Recommendation:",
        "corr_choice": "Choose the correlation type to compute:",
        "corr_analysis": "Correlation Analysis",
        "pdf_title": "6. PDF Report Export",
        "download_pdf": "Download PDF Report",
        "insufficient_data": "Insufficient data for correlation analysis. Need at least 3 valid pairs.",
        "upload_info": "👆 Please upload a CSV or Excel file to begin the analysis.",
        "unsupported_format": "Unsupported file format. Please upload CSV or Excel file.",
        "error_loading": "Failed to load dataset. Please check your file format.",
        "reco_pearson": "Use Pearson correlation because X_total and Y_total meet normality (p ≥ 0.05).",
        "reco_spearman": "Use Spearman correlation because at least one variable is non-normal and/or ordinal.",
    },
    "zh": {
        "label": "中文",
        "page_title": "统计学1问卷分析",
        "header_title": "统计学1问卷分析应用",
        "header_subtitle": "课程：统计学1 | 讲师：Dr. Edwin Setiawan Nugraha",
        "nav_title": "导航",
        "steps_title": "步骤：",
        "step1": "上传数据集",
        "step2": "选择变量",
        "step3": "查看结果",
        "members_title": "小组成员",
        "dataset_section_title": "1. 上传数据集",
        "upload_label": "上传您的数据集（CSV 或 Excel）",
        "dataset_loaded": "数据集加载成功！形状：{rows} 行 × {cols} 列",
        "view_raw": "查看原始数据集",
        "variable_selection_title": "2. 变量选择",
        "independent_label": "自变量 (X)",
        "dependent_label": "因变量 (Y)",
        "select_x": "选择自变量 X 的列（李克特量表条目）",
        "select_y": "选择因变量 Y 的列（李克特量表条目）",
        "select_warning": "请至少为变量 X 和变量 Y 各选择一列。",
        "composite_success": "已计算综合得分：X_total (n={nx})，Y_total (n={ny})",
        "descriptive_title": "3. 描述性统计",
        "variable_x_items": "变量 X 条目",
        "variable_y_items": "变量 Y 条目",
        "composite_section": "综合得分（X_total 和 Y_total）",
        "visual_title": "4. 可视化",
        "hist_x": "直方图：X_total",
        "hist_y": "直方图：Y_total",
        "boxplots": "箱线图",
        "scatter": "散点图：X_total 对 Y_total",
        "association_title": "5. 关系分析",
        "assumption_checks": "假设检验",
        "normality_x": "X_total 正态性检验",
        "normality_y": "Y_total 正态性检验",
        "recommendation_title": "相关方法推荐：",
        "corr_choice": "选择要计算的相关类型：",
        "corr_analysis": "相关分析",
        "pdf_title": "6. 导出 PDF 报告",
        "download_pdf": "下载 PDF 报告",
        "insufficient_data": "相关分析的数据不足。至少需要 3 对有效数据。",
        "upload_info": "👆 请上传 CSV 或 Excel 文件以开始分析。",
        "unsupported_format": "不支持的文件格式。请上传 CSV 或 Excel 文件。",
        "error_loading": "加载数据集失败。请检查文件格式。",
        "reco_pearson": "当 X_total 和 Y_total 满足正态性假设 (p ≥ 0.05) 时，推荐使用皮尔逊相关。",
        "reco_spearman": "当至少一个变量不满足正态性且/或为有序尺度时，推荐使用斯皮尔曼相关。",
    },
    "ja": {
        "label": "日本語",
        "page_title": "統計学1アンケート分析",
        "header_title": "統計学1アンケート分析アプリケーション",
        "header_subtitle": "科目：統計学1 | 担当教員：Dr. Edwin Setiawan Nugraha",
        "nav_title": "ナビゲーション",
        "steps_title": "ステップ：",
        "step1": "データセットをアップロード",
        "step2": "変数を選択",
        "step3": "結果を表示",
        "members_title": "グループメンバー",
        "dataset_section_title": "1. データセットのアップロード",
        "upload_label": "データセットをアップロードしてください（CSV または Excel）",
        "dataset_loaded": "データセットの読み込みに成功しました！ 形状：{rows} 行 × {cols} 列",
        "view_raw": "生データセットを表示",
        "variable_selection_title": "2. 変数の選択",
        "independent_label": "独立変数 (X)",
        "dependent_label": "従属変数 (Y)",
        "select_x": "独立変数 X 用の列を選択（リッカート尺度項目）",
        "select_y": "従属変数 Y 用の列を選択（リッカート尺度項目）",
        "select_warning": "X と Y の両方に少なくとも1つの列を選択してください。",
        "composite_success": "合成得点を計算しました：X_total (n={nx})，Y_total (n={ny})",
        "descriptive_title": "3. 記述統計",
        "variable_x_items": "変数 X の項目",
        "variable_y_items": "変数 Y の項目",
        "composite_section": "合成得点（X_total と Y_total）",
        "visual_title": "4. 可視化",
        "hist_x": "ヒストグラム：X_total",
        "hist_y": "ヒストグラム：Y_total",
        "boxplots": "箱ひげ図",
        "scatter": "散布図：X_total vs Y_total",
        "association_title": "5. 関連分析",
        "assumption_checks": "仮定の検定",
        "normality_x": "X_total 正規性検定",
        "normality_y": "Y_total 正規性検定",
        "recommendation_title": "相関手法の推奨：",
        "corr_choice": "計算する相関の種類を選択：",
        "corr_analysis": "相関分析",
        "pdf_title": "6. PDF レポートのエクスポート",
        "download_pdf": "PDF レポートをダウンロード",
        "insufficient_data": "相関分析に十分なデータがありません。少なくとも3組の有効なペアが必要です。",
        "upload_info": "👆 分析を開始するには CSV または Excel ファイルをアップロードしてください。",
        "unsupported_format": "サポートされていないファイル形式です。CSV または Excel ファイルをアップロードしてください。",
        "error_loading": "データセットの読み込みに失敗しました。ファイル形式を確認してください。",
        "reco_pearson": "X_total と Y_total が正規性を満たす場合 (p ≥ 0.05)、ピアソンの相関を使用してください。",
        "reco_spearman": "少なくとも一方の変数が正規分布でない、または順序尺度の場合、スピアマンの相関を使用してください。",
    },
    "ko": {
        "label": "한국어",
        "page_title": "통계학 1 설문 분석",
        "header_title": "통계학 1 설문 분석 애플리케이션",
        "header_subtitle": "과목: 통계학 1 | 담당 교수: Dr. Edwin Setiawan Nugraha",
        "nav_title": "내비게이션",
        "steps_title": "단계:",
        "step1": "데이터셋 업로드",
        "step2": "변수 선택",
        "step3": "결과 보기",
        "members_title": "조원",
        "dataset_section_title": "1. 데이터셋 업로드",
        "upload_label": "데이터셋을 업로드하세요 (CSV 또는 Excel)",
        "dataset_loaded": "데이터셋이 성공적으로 불러와졌습니다! 형태: {rows}행 × {cols}열",
        "view_raw": "원시 데이터셋 보기",
        "variable_selection_title": "2. 변수 선택",
        "independent_label": "독립 변수 (X)",
        "dependent_label": "종속 변수 (Y)",
        "select_x": "독립 변수 X를 위한 열 선택 (리커트 척도 문항)",
        "select_y": "종속 변수 Y를 위한 열 선택 (리커트 척도 문항)",
        "select_warning": "X와 Y 각각에 대해 최소 한 개의 열을 선택하세요.",
        "composite_success": "합성 점수 계산 완료: X_total (n={nx}), Y_total (n={ny})",
        "descriptive_title": "3. 기술통계",
        "variable_x_items": "변수 X 문항",
        "variable_y_items": "변수 Y 문항",
        "composite_section": "합성 점수 (X_total 및 Y_total)",
        "visual_title": "4. 시각화",
        "hist_x": "히스토그램: X_total",
        "hist_y": "히스토그램: Y_total",
        "boxplots": "박스플롯",
        "scatter": "산점도: X_total vs Y_total",
        "association_title": "5. 관계 분석",
        "assumption_checks": "가정 검정",
        "normality_x": "X_total 정규성 검정",
        "normality_y": "Y_total 정규성 검정",
        "recommendation_title": "상관분석 방법 추천:",
        "corr_choice": "계산할 상관 유형을 선택하세요:",
        "corr_analysis": "상관 분석",
        "pdf_title": "6. PDF 보고서 내보내기",
        "download_pdf": "PDF 보고서 다운로드",
        "insufficient_data": "상관 분석을 위한 데이터가 부족합니다. 최소 3쌍의 유효한 데이터가 필요합니다.",
        "upload_info": "👆 분석을 시작하려면 CSV 또는 Excel 파일을 업로드하세요.",
        "unsupported_format": "지원되지 않는 파일 형식입니다. CSV 또는 Excel 파일을 업로드하세요.",
        "error_loading": "데이터셋을 불러오지 못했습니다. 파일 형식을 확인하세요.",
        "reco_pearson": "X_total과 Y_total이 정규성을 만족하는 경우 (p ≥ 0.05), 피어슨 상관을 사용하세요.",
        "reco_spearman": "적어도 한 변수라도 정규성을 만족하지 않거나 서열 척도인 경우, 스피어만 상관을 사용하세요.",
    },
    "de": {
        "label": "Deutsch",
        "page_title": "Statistik 1 Umfrageanalyse",
        "header_title": "Statistik 1 Umfrageanalyse Anwendung",
        "header_subtitle": "Kurs: Statistik 1 | Dozent: Dr. Edwin Setiawan Nugraha",
        "nav_title": "Navigation",
        "steps_title": "Schritte:",
        "step1": "Datensatz hochladen",
        "step2": "Variablen wählen",
        "step3": "Ergebnisse anzeigen",
        "members_title": "Gruppenmitglieder",
        "dataset_section_title": "1. Datensatz hochladen",
        "upload_label": "Laden Sie Ihren Datensatz hoch (CSV oder Excel)",
        "dataset_loaded": "Datensatz erfolgreich geladen! Form: {rows} Zeilen × {cols} Spalten",
        "view_raw": "Rohdatensatz anzeigen",
        "variable_selection_title": "2. Variablenauswahl",
        "independent_label": "Unabhängige Variable (X)",
        "dependent_label": "Abhängige Variable (Y)",
        "select_x": "Spalten für Variable X wählen (Likert-Skalen-Items)",
        "select_y": "Spalten für Variable Y wählen (Likert-Skalen-Items)",
        "select_warning": "Bitte wählen Sie mindestens eine Spalte für X und Y.",
        "composite_success": "Komposit-Scores berechnet: X_total (n={nx}), Y_total (n={ny})",
        "descriptive_title": "3. Deskriptive Statistik",
        "variable_x_items": "Variable X Items",
        "variable_y_items": "Variable Y Items",
        "composite_section": "Komposit-Scores (X_total und Y_total)",
        "visual_title": "4. Visualisierungen",
        "hist_x": "Histogramm: X_total",
        "hist_y": "Histogramm: Y_total",
        "boxplots": "Boxplots",
        "scatter": "Streudiagramm: X_total vs Y_total",
        "association_title": "5. Zusammenhangsanalyse",
        "assumption_checks": "Prüfung der Annahmen",
        "normality_x": "X_total Normalitätstest",
        "normality_y": "Y_total Normalitätstest",
        "recommendation_title": "Empfohlene Korrelationsmethode:",
        "corr_choice": "Wählen Sie den zu berechnenden Korrelations-Typ:",
        "corr_analysis": "Korrelationsanalyse",
        "pdf_title": "6. PDF-Bericht exportieren",
        "download_pdf": "PDF-Bericht herunterladen",
        "insufficient_data": "Unzureichende Daten für die Korrelationsanalyse. Mindestens 3 gültige Paare erforderlich.",
        "upload_info": "👆 Bitte laden Sie eine CSV- oder Excel-Datei hoch, um zu beginnen.",
        "unsupported_format": "Nicht unterstütztes Dateiformat. Bitte laden Sie eine CSV- oder Excel-Datei hoch.",
        "error_loading": "Datensatz konnte nicht geladen werden. Bitte prüfen Sie das Dateiformat.",
        "reco_pearson": "Verwenden Sie die Pearson-Korrelation, da X_total und Y_total die Normalität erfüllen (p ≥ 0.05).",
        "reco_spearman": "Verwenden Sie die Spearman-Korrelation, da mindestens eine Variable nicht normalverteilt ist und/oder ordinal ist.",
    },
    "nl": {
        "label": "Nederlands",
        "page_title": "Statistiek 1 Enquête-analyse",
        "header_title": "Statistiek 1 Enquête-analyse Applicatie",
        "header_subtitle": "Vak: Statistiek 1 | Docent: Dr. Edwin Setiawan Nugraha",
        "nav_title": "Navigatie",
        "steps_title": "Stappen:",
        "step1": "Dataset uploaden",
        "step2": "Variabelen kiezen",
        "step3": "Resultaten bekijken",
        "members_title": "Groepsleden",
        "dataset_section_title": "1. Dataset uploaden",
        "upload_label": "Upload uw dataset (CSV of Excel)",
        "dataset_loaded": "Dataset succesvol geladen! Vorm: {rows} rijen × {cols} kolommen",
        "view_raw": "Ruwe dataset bekijken",
        "variable_selection_title": "2. Variabelenselectie",
        "independent_label": "Onafhankelijke variabele (X)",
        "dependent_label": "Afhankelijke variabele (Y)",
        "select_x": "Kies kolommen voor variabele X (Likert-schaalitems)",
        "select_y": "Kies kolommen voor variabele Y (Likert-schaalitems)",
        "select_warning": "Selecteer ten minste één kolom voor zowel X als Y.",
        "composite_success": "Samengestelde scores berekend: X_total (n={nx}), Y_total (n={ny})",
        "descriptive_title": "3. Beschrijvende statistiek",
        "variable_x_items": "Variabele X-items",
        "variable_y_items": "Variabele Y-items",
        "composite_section": "Samengestelde scores (X_total en Y_total)",
        "visual_title": "4. Visualisaties",
        "hist_x": "Histogram: X_total",
        "hist_y": "Histogram: Y_total",
        "boxplots": "Boxplots",
        "scatter": "Spreidingsdiagram: X_total vs Y_total",
        "association_title": "5. Verbandanalyse",
        "assumption_checks": "Aannames controleren",
        "normality_x": "X_total normaliteitstoets",
        "normality_y": "Y_total normaliteitstoets",
        "recommendation_title": "Aanbevolen correlatiemethode:",
        "corr_choice": "Kies het type correlatie dat u wilt berekenen:",
        "corr_analysis": "Correlatie-analyse",
        "pdf_title": "6. PDF-rapport exporteren",
        "download_pdf": "PDF-rapport downloaden",
        "insufficient_data": "Onvoldoende gegevens voor correlatie-analyse. Minstens 3 geldige paren nodig.",
        "upload_info": "👆 Upload een CSV- of Excel-bestand om de analyse te starten.",
        "unsupported_format": "Niet-ondersteund bestandsformaat. Upload een CSV- of Excel-bestand.",
        "error_loading": "Laden van de dataset mislukt. Controleer het bestandsformaat.",
        "reco_pearson": "Gebruik Pearson-correlatie omdat X_total en Y_total aan normaliteit voldoen (p ≥ 0.05).",
        "reco_spearman": "Gebruik Spearman-correlatie omdat ten minste één variabele niet normaal is en/of ordinaal is.",
    },
    "ru": {
        "label": "Русский",
        "page_title": "Анализ опроса по статистике 1",
        "header_title": "Приложение для анализа опроса по статистике 1",
        "header_subtitle": "Курс: Статистика 1 | Преподаватель: Dr. Edwin Setiawan Nugraha",
        "nav_title": "Навигация",
        "steps_title": "Шаги:",
        "step1": "Загрузить датасет",
        "step2": "Выбрать переменные",
        "step3": "Просмотреть результаты",
        "members_title": "Члены группы",
        "dataset_section_title": "1. Загрузка датасета",
        "upload_label": "Загрузите ваш датасет (CSV или Excel)",
        "dataset_loaded": "Датасет успешно загружен! Размер: {rows} строк × {cols} столбцов",
        "view_raw": "Показать исходный датасет",
        "variable_selection_title": "2. Выбор переменных",
        "independent_label": "Независимая переменная (X)",
        "dependent_label": "Зависимая переменная (Y)",
        "select_x": "Выберите столбцы для переменной X (пункты по шкале Лайкерта)",
        "select_y": "Выберите столбцы для переменной Y (пункты по шкале Лайкерта)",
        "select_warning": "Выберите как минимум один столбец для X и Y.",
        "composite_success": "Сводные показатели рассчитаны: X_total (n={nx}), Y_total (n={ny})",
        "descriptive_title": "3. Описательная статистика",
        "variable_x_items": "Пункты переменной X",
        "variable_y_items": "Пункты переменной Y",
        "composite_section": "Сводные показатели (X_total и Y_total)",
        "visual_title": "4. Визуализация",
        "hist_x": "Гистограмма: X_total",
        "hist_y": "Гистограмма: Y_total",
        "boxplots": "Ящик с усами (boxplot)",
        "scatter": "Диаграмма рассеяния: X_total vs Y_total",
        "association_title": "5. Анализ взаимосвязи",
        "assumption_checks": "Проверка предположений",
        "normality_x": "Проверка нормальности X_total",
        "normality_y": "Проверка нормальности Y_total",
        "recommendation_title": "Рекомендация по методу корреляции:",
        "corr_choice": "Выберите тип корреляции для расчёта:",
        "corr_analysis": "Корреляционный анализ",
        "pdf_title": "6. Экспорт PDF-отчёта",
        "download_pdf": "Скачать PDF-отчёт",
        "insufficient_data": "Недостаточно данных для корреляционного анализа. Требуется минимум 3 пары наблюдений.",
        "upload_info": "👆 Пожалуйста, загрузите файл CSV или Excel, чтобы начать анализ.",
        "unsupported_format": "Неподдерживаемый формат файла. Пожалуйста, загрузите файл CSV или Excel.",
        "error_loading": "Не удалось загрузить датасет. Проверьте формат файла.",
        "reco_pearson": "Используйте корреляцию Пирсона, если X_total и Y_total удовлетворяют нормальному распределению (p ≥ 0.05).",
        "reco_spearman": "Используйте корреляцию Спирмена, если хотя бы одна переменная не нормально распределена и/или является порядковой.",
    },
}

def translate(lang_code: str, key: str, fallback: str = ""):
    lang_pack = LANG_OPTIONS.get(lang_code, LANG_OPTIONS["en"])
    default_pack = LANG_OPTIONS["en"]
    return lang_pack.get(key) or default_pack.get(key) or fallback or key

# ---------------------------------------------------------
# Language picker (sidebar)
# ---------------------------------------------------------
lang_code = st.sidebar.selectbox(
    "Language / Bahasa",
    options=list(LANG_OPTIONS.keys()),
    format_func=lambda code: LANG_OPTIONS[code]["label"],
    index=0,
)
t = lambda key, fallback="": translate(lang_code, key, fallback)

# ---------------------------------------------------------
# Background video ala Matrix app (using local BG.mp4)
# ---------------------------------------------------------
video_path = Path("BG.mp4")
if video_path.exists():
    video_bytes = video_path.read_bytes()
    video_base64 = base64.b64encode(video_bytes).decode()
    video_src = f"data:video/mp4;base64,{video_base64}"
else:
    video_src = ""

video_html = f"""
<style>
#myVideo {{
  position: fixed;
  right: 0;
  bottom: 0;
  min-width: 100%;
  min-height: 100%;
  width: auto;
  height: auto;
  z-index: -1;
  object-fit: cover;
  opacity: 0.9;
}}
.stApp {{
  background: transparent;
}}
[data-testid="stHeader"] {{
  background: rgba(255, 255, 255, 0.05) !important;
  backdrop-filter: blur(10px) !important;
}}
[data-testid="stSidebar"] > div:first-child {{
  background: rgba(255, 255, 255, 0.1) !important;
  backdrop-filter: blur(20px) saturate(180%) !important;
  border-right: 1px solid rgba(255, 255, 255, 0.2) !important;
}}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
  background: transparent !important;
}}
</style>

<video autoplay muted loop playsinline id="myVideo">
  <source src="{video_src}" type="video/mp4">
</video>
"""

st.markdown(video_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# Global CSS (Times New Roman + styling + warna teks + animasi)
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.02);
        }
    }
    
    @keyframes shimmer {
        0% {
            background-position: -1000px 0;
        }
        100% {
            background-position: 1000px 0;
        }
    }
    
    html, body, [class*="css"]  {
        font-family: "Times New Roman", Times, serif;
    }

    /* Glass badge transparan dengan auto text color */
    .glass-badge-inline {
        display: inline-block;
        padding: 10px 16px;
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(20px) saturate(180%);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        animation: fadeInUp 0.6s ease-out;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .glass-badge-inline::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        animation: shimmer 3s infinite;
    }
    
    .glass-badge-inline:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
        background: rgba(255, 255, 255, 0.2);
    }

    /* Badge untuk semua teks */
    .text-badge {
        display: inline-block;
        padding: 8px 14px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(16px) saturate(160%);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        animation: fadeIn 0.5s ease-out;
        margin: 2px;
    }
    
    /* Badge untuk metrics */
    .metric-badge {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.18);
        backdrop-filter: blur(14px);
        border-radius: 10px;
        padding: 12px;
        animation: fadeInUp 0.5s ease-out;
        transition: all 0.3s ease;
    }
    
    .metric-badge:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }

    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        background: rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        padding: 16px 24px;
        border: 1px solid rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(20px) saturate(180%);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        animation: fadeInUp 0.8s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
        animation: shimmer 4s infinite;
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
        background: rgba(255, 255, 255, 0.1);
        padding: 14px 20px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.22);
        backdrop-filter: blur(18px) saturate(170%);
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.25);
        animation: slideInLeft 0.6s ease-out;
        position: relative;
    }
    
    .sub-section {
        font-size: 1.2rem;
        font-weight: bold;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        background: rgba(255, 255, 255, 0.08);
        padding: 12px 18px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        backdrop-filter: blur(16px) saturate(160%);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        animation: fadeInUp 0.5s ease-out;
    }
    
    .member-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(16px) saturate(160%);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
        animation: slideInRight 0.6s ease-out;
        transition: all 0.3s ease;
    }
    
    .member-card:hover {
        transform: translateX(5px);
        background: rgba(255, 255, 255, 0.15);
        box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35);
    }
    
    .member-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;
    }
    
    .member-photo {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.15);
        border: 2px solid rgba(255, 255, 255, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        text-align: center;
        padding: 4px;
        backdrop-filter: blur(10px);
    }
    
    .member-name {
        font-size: 1rem;
        font-weight: bold;
        margin: 0;
    }
    
    .member-role {
        font-size: 0.9rem;
        margin: 0;
    }
    
    .member-contrib-title {
        font-size: 0.9rem;
        font-weight: bold;
        margin-top: 4px;
        margin-bottom: 2px;
    }
    
    .member-contrib-list {
        font-size: 0.85rem;
        margin-left: 16px;
    }
    
    /* Wrapper untuk semua teks dengan badge */
    .stMarkdown p, .stMarkdown li, .stMarkdown span,
    .stText, .stDataFrame, label, h1, h2, h3, h4, h5, h6 {
        position: relative;
    }
    
    /* Info, success, warning, error boxes dengan glass effect */
    .stAlert {
        background: rgba(255, 255, 255, 0.12) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        backdrop-filter: blur(16px) saturate(160%) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
        animation: fadeIn 0.5s ease-out !important;
    }
    
    /* Metric cards dengan glass effect */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 8px !important;
        backdrop-filter: blur(12px) !important;
    }
    
    /* Input fields dengan glass effect */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: rgba(255, 255, 255, 0.12) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        backdrop-filter: blur(14px) !important;
        border-radius: 10px !important;
        color: inherit !important;
    }
    
    /* Buttons dengan glass effect */
    .stButton > button {
        background: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        backdrop-filter: blur(16px) saturate(160%) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s ease !important;
        animation: fadeIn 0.5s ease-out !important;
    }
    
    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.25) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Expander dengan glass effect */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        backdrop-filter: blur(14px) !important;
        border-radius: 10px !important;
    }
    
    /* Tabs dengan glass effect */
    [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(12px) !important;
        border-radius: 10px !important;
    }
    
    /* Dataframe dengan glass effect */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Radio buttons dengan glass effect */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 8px !important;
        backdrop-filter: blur(12px) !important;
    }
    </style>
    
    <script>
    // Function to calculate luminance and determine text color
    function getContrastColor(bgColor) {{
        // Extract RGB values
        const rgb = bgColor.match(/\\d+/g);
        if (!rgb || rgb.length < 3) return '#ffffff';
        
        // Calculate relative luminance
        const r = parseInt(rgb[0]) / 255;
        const g = parseInt(rgb[1]) / 255;
        const b = parseInt(rgb[2]) / 255;
        
        const luminance = 0.299 * r + 0.587 * g + 0.114 * b;
        
        // Return dark text for light backgrounds, light text for dark backgrounds
        return luminance > 0.5 ? '#000000' : '#ffffff';
    }}
    
    // Function to apply smart text colors to all elements
    function applySmartTextColors() {{
        // Get video element to sample background
        const video = document.getElementById('myVideo');
        if (!video || video.readyState < 2) {{
            // Fallback: use white text with dark shadow
            document.querySelectorAll('.glass-badge-inline, .text-badge, .main-header, .section-header, .sub-section, .member-card, .member-name, .member-role, .member-contrib-title, .member-contrib-list').forEach(el => {{
                el.style.color = '#ffffff';
                el.style.textShadow = '0 2px 8px rgba(0, 0, 0, 0.9), 0 0 4px rgba(0, 0, 0, 0.5)';
            });
            return;
        }}
        
        // Create canvas to sample video frame
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = Math.min(video.videoWidth || 1920, 800);
        canvas.height = Math.min(video.videoHeight || 1080, 600);
        
        // Sample multiple points across the screen for better accuracy
        const samplePoints = [
            {{x: canvas.width * 0.1, y: canvas.height * 0.1}},
            {{x: canvas.width * 0.3, y: canvas.height * 0.2}},
            {{x: canvas.width * 0.5, y: canvas.height * 0.5}},
            {{x: canvas.width * 0.7, y: canvas.height * 0.6}},
            {{x: canvas.width * 0.9, y: canvas.height * 0.9}},
            {{x: canvas.width * 0.2, y: canvas.height * 0.8}},
            {{x: canvas.width * 0.8, y: canvas.height * 0.3}}
        ];
        
        let totalLuminance = 0;
        let sampleCount = 0;
        let maxLum = 0;
        let minLum = 1;
        
        try {{
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            samplePoints.forEach(point => {{
                const imageData = ctx.getImageData(Math.floor(point.x), Math.floor(point.y), 1, 1);
                const [r, g, b] = imageData.data;
                const luminance = 0.299 * (r/255) + 0.587 * (g/255) + 0.114 * (b/255);
                totalLuminance += luminance;
                maxLum = Math.max(maxLum, luminance);
                minLum = Math.min(minLum, luminance);
                sampleCount++;
            }});
            
            const avgLuminance = totalLuminance / sampleCount;
            const contrast = maxLum - minLum;
            
            // Use average luminance, but adjust threshold based on contrast
            const threshold = contrast > 0.3 ? 0.45 : 0.5;
            const isLight = avgLuminance > threshold;
            
            const textColor = isLight ? '#000000' : '#ffffff';
            const shadowColor = isLight ? 'rgba(255, 255, 255, 0.9)' : 'rgba(0, 0, 0, 0.9)';
            const shadowColor2 = isLight ? 'rgba(255, 255, 255, 0.5)' : 'rgba(0, 0, 0, 0.5)';
            
            // Apply to all badge elements
            const shadowStyle1 = '0 2px 8px ' + shadowColor + ', 0 0 4px ' + shadowColor2;
            const shadowStyle2 = '0 1px 4px ' + shadowColor;
            const shadowStyle3 = '0 1px 3px ' + shadowColor;
            
            document.querySelectorAll('.glass-badge-inline, .text-badge, .main-header, .section-header, .sub-section').forEach(el => {{
                el.style.color = textColor;
                el.style.textShadow = shadowStyle1;
            }});
            
            // Apply to member cards
            document.querySelectorAll('.member-card, .member-name, .member-role, .member-contrib-title, .member-contrib-list').forEach(el => {{
                el.style.color = textColor;
                el.style.textShadow = shadowStyle2;
            }});
            
            // Apply to Streamlit default elements (but not those inside badges)
            document.querySelectorAll('.stMarkdown p, .stMarkdown li, .stMarkdown span, .stText, label, h1, h2, h3, h4, h5, h6').forEach(el => {{
                if (!el.closest('.glass-badge-inline') && !el.closest('.text-badge') && !el.closest('.main-header') && !el.closest('.section-header') && !el.closest('.sub-section')) {{
                    el.style.color = textColor;
                    el.style.textShadow = shadowStyle3;
                }}
            }});
        }} catch(e) {{
            // Fallback: use white text with strong shadow
            document.querySelectorAll('.glass-badge-inline, .text-badge, .main-header, .section-header, .sub-section, .member-card').forEach(el => {{
                el.style.color = '#ffffff';
                el.style.textShadow = '0 2px 8px rgba(0, 0, 0, 0.9), 0 0 4px rgba(0, 0, 0, 0.5)';
            }});
        }}
    }}
    
    // Apply colors when video is ready
    function initColorDetection() {{
        const video = document.getElementById('myVideo');
        if (video) {{
            if (video.readyState >= 2) {{
                setTimeout(applySmartTextColors, 500);
            }} else {{
                video.addEventListener('loadeddata', function() {{
                    setTimeout(applySmartTextColors, 500);
                }}, {{ once: true }});
            }}
            video.addEventListener('play', function() {{
                setTimeout(applySmartTextColors, 500);
            }}, {{ once: true }});
        }}
        
        // Apply periodically to adapt to video changes
        setInterval(applySmartTextColors, 3000);
    }}
    
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', function() {{
            setTimeout(initColorDetection, 1000);
        }});
    }} else {{
        setTimeout(initColorDetection, 1000);
    }}
    </script>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------
if "df" not in st.session_state:
    st.session_state.df = None
if "x_columns" not in st.session_state:
    st.session_state.x_columns = []
if "y_columns" not in st.session_state:
    st.session_state.y_columns = []
if "x_total" not in st.session_state:
    st.session_state.x_total = None
if "y_total" not in st.session_state:
    st.session_state.y_total = None

# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------
def load_data(file):
    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        elif file.name.endswith((".xls", ".xlsx")):
            df = pd.read_excel(file)
        else:
            st.markdown(
                f'<div class="glass-badge-inline" style="display: inline-block; margin: 10px 0;">❌ {t("unsupported_format")}</div>',
                unsafe_allow_html=True,
            )
            return None
        return df
    except Exception as e:
        st.markdown(
            f'<div class="glass-badge-inline" style="display: inline-block; margin: 10px 0;">❌ {t("error_loading")}: {str(e)}</div>',
            unsafe_allow_html=True,
        )
        return None

def compute_descriptive_stats(data, var_name):
    data_clean = data.dropna()
    if len(data_clean) == 0:
        return None, None

    stats_dict = {
        "Variable": var_name,
        "N": len(data_clean),
        "Mean": np.mean(data_clean),
        "Median": np.median(data_clean),
        "Mode": stats.mode(data_clean, keepdims=True)[0][0]
        if len(data_clean) > 0
        else np.nan,
        "Minimum": np.min(data_clean),
        "Maximum": np.max(data_clean),
        "Std Dev": np.std(data_clean, ddof=1),
        "Variance": np.var(data_clean, ddof=1),
    }

    freq_table = pd.Series(data_clean).value_counts().sort_index()
    freq_table_pct = (freq_table / len(data_clean) * 100).round(2)

    freq_df = pd.DataFrame(
        {
            "Value": freq_table.index,
            "Frequency": freq_table.values,
            "Percentage": freq_table_pct.values,
        }
    )
    return stats_dict, freq_df

def interpret_correlation(r, p_value):
    direction = "positive" if r > 0 else "negative"
    abs_r = abs(r)
    if abs_r < 0.3:
        strength = "weak"
    elif abs_r < 0.7:
        strength = "moderate"
    else:
        strength = "strong"

    if p_value < 0.001:
        sig_text = "highly significant (p < 0.001)"
    elif p_value < 0.01:
        sig_text = "very significant (p < 0.01)"
    elif p_value < 0.05:
        sig_text = "significant (p < 0.05)"
    else:
        sig_text = "not significant (p ≥ 0.05)"

    interpretation = (
        f"The correlation is {direction} and {strength} (r = {r:.4f}), "
        f"and it is {sig_text}."
    )
    return direction, strength, sig_text, interpretation

def check_normality(data):
    data_clean = data.dropna()
    if len(data_clean) < 3 or len(data_clean) > 5000:
        return None, None, "Sample size too small or too large for Shapiro-Wilk test."

    statistic, p_value = shapiro(data_clean)
    is_normal = p_value > 0.05

    interpretation = f"Shapiro-Wilk test: W = {statistic:.4f}, p = {p_value:.4f}. "
    if is_normal:
        interpretation += "Data appears to be normally distributed (p > 0.05)."
    else:
        interpretation += (
            "Data does not appear to be normally distributed (p ≤ 0.05). "
            "Consider using Spearman correlation."
        )
    return statistic, p_value, interpretation

def generate_pdf_report(
    df,
    x_columns,
    y_columns,
    x_total,
    y_total,
    x_stats,
    y_stats,
    x_freq,
    y_freq,
    correlation_r,
    correlation_p,
    interpretation,
    normality_x,
    normality_y,
    lang_code,
):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []

    # helper terjemahan lokal untuk PDF
    _t = lambda key, fallback="": translate(lang_code, key, fallback)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontName="Times-Roman",
        fontSize=18,
        textColor=colors.HexColor("#1f77b4"),
        spaceAfter=30,
        alignment=TA_CENTER,
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontName="Times-Roman",
        fontSize=14,
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=12,
        spaceBefore=12,
    )
    normal_style = ParagraphStyle(
        "CustomNormal",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=11,
    )

    story.append(Paragraph(_t("page_title", "Statistics 1 Survey Analysis"), title_style))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph(_t("pdf_course_label", "Course: Statistics 1"), normal_style))
    story.append(
        Paragraph(
            _t(
                "pdf_lecturer_label",
                "Lecturer: Dr. Edwin Setiawan Nugraha",
            ),
            normal_style,
        )
    )
    story.append(Spacer(1, 0.3 * inch))

    story.append(
        Paragraph(_t("pdf_variables_title", "Variables Description"), heading_style)
    )
    story.append(
        Paragraph(
            f"<b>{_t('independent_label', 'Independent Variable (X)')}:</b> "
            f"{', '.join(x_columns)}",
            normal_style,
        )
    )
    story.append(
        Paragraph(
            f"<b>{_t('dependent_label', 'Dependent Variable (Y)')}:</b> "
            f"{', '.join(y_columns)}",
            normal_style,
        )
    )
    story.append(
        Paragraph(
            _t("pdf_x_total_desc", "<b>X_total:</b> Mean of X items"), normal_style
        )
    )
    story.append(
        Paragraph(
            _t("pdf_y_total_desc", "<b>Y_total:</b> Mean of Y items"), normal_style
        )
    )
    story.append(Spacer(1, 0.2 * inch))

    story.append(
        Paragraph(_t("descriptive_title", "Descriptive Statistics"), heading_style)
    )

    if x_stats:
        story.append(Paragraph("<b>X_total:</b>", normal_style))
        stats_text = (
            f"{_t('mean_label', 'Mean')}: {x_stats['Mean']:.4f}, "
            f"{_t('median_label', 'Median')}: {x_stats['Median']:.4f}, "
            f"{_t('std_label', 'Std Dev')}: {x_stats['Std Dev']:.4f}, "
            f"{_t('min_label', 'Min')}: {x_stats['Minimum']:.4f}, "
            f"{_t('max_label', 'Max')}: {x_stats['Maximum']:.4f}"
        )
        story.append(Paragraph(stats_text, normal_style))
        story.append(Spacer(1, 0.1 * inch))

    if y_stats:
        story.append(Paragraph("<b>Y_total:</b>", normal_style))
        stats_text = (
            f"{_t('mean_label', 'Mean')}: {y_stats['Mean']:.4f}, "
            f"{_t('median_label', 'Median')}: {y_stats['Median']:.4f}, "
            f"{_t('std_label', 'Std Dev')}: {y_stats['Std Dev']:.4f}, "
            f"{_t('min_label', 'Min')}: {y_stats['Minimum']:.4f}, "
            f"{_t('max_label', 'Max')}: {y_stats['Maximum']:.4f}"
        )
        story.append(Paragraph(stats_text, normal_style))
        story.append(Spacer(1, 0.2 * inch))

    story.append(
        Paragraph(
            _t("association_title", "Association Analysis"),
            heading_style,
        )
    )
    story.append(
        Paragraph(
            f"<b>{_t('pdf_corr_label', 'Correlation Coefficient (r)')}:</b> "
            f"{correlation_r:.4f}",
            normal_style,
        )
    )
    story.append(
        Paragraph(
            f"<b>{_t('pdf_pvalue_label', 'p-value')}:</b> {correlation_p:.4f}",
            normal_style,
        )
    )
    story.append(
        Paragraph(
            f"<b>{_t('pdf_interpretation_label', 'Interpretation')}:</b> "
            f"{interpretation}",
            normal_style,
        )
    )
    story.append(Spacer(1, 0.2 * inch))

    story.append(
        Paragraph(
            _t("assumption_checks", "Assumption Checks"),
            heading_style,
        )
    )
    if normality_x:
        story.append(
            Paragraph(
                f"<b>{_t('normality_x', 'X_total Normality')}:</b> {normality_x}",
                normal_style,
            )
        )
    if normality_y:
        story.append(
            Paragraph(
                f"<b>{_t('normality_y', 'Y_total Normality')}:</b> {normality_y}",
                normal_style,
            )
        )

    # -------------------------------------------------
    # Tambahkan grafik ke PDF (histogram, boxplot, scatter)
    # -------------------------------------------------
    story.append(Spacer(1, 0.3 * inch))
    story.append(
        Paragraph(_t("visual_title", "Visualizations"), heading_style)
    )

    # Histogram X_total
    if x_total is not None:
        fig_hx, ax_hx = plt.subplots(figsize=(5, 3))
        ax_hx.hist(
            x_total.dropna(),
            bins=20,
            edgecolor="black",
            alpha=0.7,
            color="#60a5fa",
        )
        ax_hx.set_xlabel("X_total")
        ax_hx.set_ylabel("Frequency")
        ax_hx.set_title(_t("hist_x", "Histogram: X_total"))
        ax_hx.grid(True, alpha=0.3)

        img_buf_hx = BytesIO()
        fig_hx.savefig(img_buf_hx, format="png", bbox_inches="tight")
        plt.close(fig_hx)
        img_buf_hx.seek(0)
        story.append(RLImage(img_buf_hx, width=5.5 * inch))
        story.append(Spacer(1, 0.2 * inch))

    # Histogram Y_total
    if y_total is not None:
        fig_hy, ax_hy = plt.subplots(figsize=(5, 3))
        ax_hy.hist(
            y_total.dropna(),
            bins=20,
            edgecolor="black",
            alpha=0.7,
            color="#f97373",
        )
        ax_hy.set_xlabel("Y_total")
        ax_hy.set_ylabel("Frequency")
        ax_hy.set_title(_t("hist_y", "Histogram: Y_total"))
        ax_hy.grid(True, alpha=0.3)

        img_buf_hy = BytesIO()
        fig_hy.savefig(img_buf_hy, format="png", bbox_inches="tight")
        plt.close(fig_hy)
        img_buf_hy.seek(0)
        story.append(RLImage(img_buf_hy, width=5.5 * inch))
        story.append(Spacer(1, 0.2 * inch))

    # Boxplots X_total & Y_total
    if x_total is not None and y_total is not None:
        fig_bx, (ax_bx1, ax_bx2) = plt.subplots(1, 2, figsize=(7, 3))
        ax_bx1.boxplot(x_total.dropna(), vert=True)
        ax_bx1.set_ylabel("X_total")
        ax_bx1.set_title("Boxplot X_total")
        ax_bx1.grid(True, alpha=0.3)

        ax_bx2.boxplot(y_total.dropna(), vert=True)
        ax_bx2.set_ylabel("Y_total")
        ax_bx2.set_title("Boxplot Y_total")
        ax_bx2.grid(True, alpha=0.3)

        img_buf_bx = BytesIO()
        fig_bx.savefig(img_buf_bx, format="png", bbox_inches="tight")
        plt.close(fig_bx)
        img_buf_bx.seek(0)
        story.append(RLImage(img_buf_bx, width=5.5 * inch))
        story.append(Spacer(1, 0.2 * inch))

    # Scatter plot X_total vs Y_total
    if x_total is not None and y_total is not None:
        valid_df = (
            pd.DataFrame({"X": x_total, "Y": y_total})
            .dropna()
        )
        if not valid_df.empty:
            fig_sc, ax_sc = plt.subplots(figsize=(5.5, 3.5))
            ax_sc.scatter(valid_df["X"], valid_df["Y"], alpha=0.6, color="#22c55e")
            ax_sc.set_xlabel("X_total")
            ax_sc.set_ylabel("Y_total")
            ax_sc.set_title(_t("scatter", "Scatter Plot: X_total vs Y_total"))
            ax_sc.grid(True, alpha=0.3)

            img_buf_sc = BytesIO()
            fig_sc.savefig(img_buf_sc, format="png", bbox_inches="tight")
            plt.close(fig_sc)
            img_buf_sc.seek(0)
            story.append(RLImage(img_buf_sc, width=5.5 * inch))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ---------------------------------------------------------
# Main header
# ---------------------------------------------------------
st.markdown(
    f'<p class="main-header">{t("header_title")}</p>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<p class="glass-badge-inline" style="display:block; text-align: center; margin: 0 auto; width: fit-content; font-size: 1.1rem;">{t("header_subtitle")}</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# ---------------------------------------------------------
# Sidebar: Navigation + Group Members
# ---------------------------------------------------------
st.sidebar.markdown(
    f'<div class="glass-badge-inline" style="font-size:1.2rem;font-weight:700;">{t("nav_title")}</div>',
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    f'<div class="glass-badge-inline" style="margin-top:8px; font-weight:700;">{t("steps_title")}</div>',
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    f'<div class="glass-badge-inline" style="margin-top:6px;">1. {t("step1")}</div>',
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    f'<div class="glass-badge-inline" style="margin-top:6px;">2. {t("step2")}</div>',
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    f'<div class="glass-badge-inline" style="margin-top:6px;">3. {t("step3")}</div>',
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    f'<div class="glass-badge-inline" style="font-weight:700;">{t("members_title")}</div>',
    unsafe_allow_html=True,
)

def load_member_photo(first_name: str):
    img_path = Path(f"{first_name}.jpg")
    if img_path.exists():
        return Image.open(img_path)
    return None

# 1. Aldy Candra Winata
with st.sidebar.container():
    st.markdown(
        '<div class="member-card" style="padding: 12px;">',
        unsafe_allow_html=True,
    )
    col_photo, col_info = st.columns([1, 2])
    with col_photo:
        img = load_member_photo("Aldy")
        if img is not None:
            st.image(img, width=56)
        else:
            st.markdown(
                '<div class="member-photo">No<br>Photo</div>',
                unsafe_allow_html=True,
            )
    with col_info:
        st.markdown('<p class="member-name">Aldy Candra Winata</p>', unsafe_allow_html=True)
        st.markdown('<p class="member-role">Role: Project Leader</p>', unsafe_allow_html=True)

    st.markdown('<p class="member-contrib-title">Contribution:</p>', unsafe_allow_html=True)
    st.markdown(
        """
        <ul class="member-contrib-list">
            <li>Overall project coordination</li>
            <li>Research framework & questionnaire design</li>
            <li>Final report editing</li>
        </ul>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# 2. Mitza Cetta Cadudasa
with st.sidebar.container():
    st.markdown(
        '<div class="member-card" style="padding: 12px;">',
        unsafe_allow_html=True,
    )
    col_photo, col_info = st.columns([1, 2])
    with col_photo:
        img = load_member_photo("Mitza")
        if img is not None:
            st.image(img, width=56)
        else:
            st.markdown(
                '<div class="member-photo">No<br>Photo</div>',
                unsafe_allow_html=True,
            )
    with col_info:
        st.markdown('<p class="member-name">Mitza Cetta Cadudasa</p>', unsafe_allow_html=True)
        st.markdown('<p class="member-role">Role: Data Engineer</p>', unsafe_allow_html=True)

    st.markdown('<p class="member-contrib-title">Contribution:</p>', unsafe_allow_html=True)
    st.markdown(
        """
        <ul class="member-contrib-list">
            <li>Dataset collection, cleaning, and preprocessing</li>
            <li>Implementation of the Streamlit application</li>
            <li>Integration of visualizations and layout</li>
        </ul>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# 3. Miftahul Khaerunnisa
with st.sidebar.container():
    st.markdown(
        '<div class="member-card" style="padding: 12px;">',
        unsafe_allow_html=True,
    )
    col_photo, col_info = st.columns([1, 2])
    with col_photo:
        img = load_member_photo("Miftahul")
        if img is not None:
            st.image(img, width=56)
        else:
            st.markdown(
                '<div class="member-photo">No<br>Photo</div>',
                unsafe_allow_html=True,
            )
    with col_info:
        st.markdown('<p class="member-name">Miftahul Khaerunnisa</p>', unsafe_allow_html=True)
        st.markdown('<p class="member-role">Role: Statistician</p>', unsafe_allow_html=True)

    st.markdown('<p class="member-contrib-title">Contribution:</p>', unsafe_allow_html=True)
    st.markdown(
        """
        <ul class="member-contrib-list">
            <li>Selection of statistical methods</li>
            <li>Normality, descriptive, and correlation analysis</li>
            <li>Interpretation of statistical results</li>
        </ul>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# 4. Fauziah Fithriyani Pamuji
with st.sidebar.container():
    st.markdown(
        '<div class="member-card" style="padding: 12px;">',
        unsafe_allow_html=True,
    )
    col_photo, col_info = st.columns([1, 2])
    with col_photo:
        img = load_member_photo("Fauziah")
        if img is not None:
            st.image(img, width=56)
        else:
            st.markdown(
                '<div class="member-photo">No<br>Photo</div>',
                unsafe_allow_html=True,
            )
    with col_info:
        st.markdown('<p class="member-name">Fauziah Fithriyani Pamuji</p>', unsafe_allow_html=True)
        st.markdown('<p class="member-role">Role: Documentation & Design</p>', unsafe_allow_html=True)

    st.markdown('<p class="member-contrib-title">Contribution:</p>', unsafe_allow_html=True)
    st.markdown(
        """
        <ul class="member-contrib-list">
            <li>UI/UX design of the web application</li>
            <li>Preparation of presentation slides</li>
            <li>Supporting documentation and proofreading</li>
        </ul>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Section 1: Dataset Upload
# ---------------------------------------------------------
st.markdown(
    f'<p class="section-header">{t("dataset_section_title")}</p>',
    unsafe_allow_html=True,
)
uploaded_file = st.file_uploader(
    t("upload_label"), type=["csv", "xlsx", "xls"]
)

if uploaded_file is not None:
    df = load_data(uploaded_file)
    if df is not None:
        st.session_state.df = df

        st.markdown(
            f'<div class="glass-badge-inline" style="display: inline-block; margin: 10px 0;">✅ {t("dataset_loaded").format(rows=df.shape[0], cols=df.shape[1])}</div>',
            unsafe_allow_html=True,
        )

        with st.expander(t("view_raw"), expanded=False):
            st.dataframe(df, use_container_width=True)

        # -------------------------------------------------
        # Section 2: Variable Selection
        # -------------------------------------------------
        st.markdown(
            f'<p class="section-header">{t("variable_selection_title")}</p>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f'<p class="sub-section">{t("independent_label")}</p>',
                unsafe_allow_html=True,
            )
            x_columns = st.multiselect(
                t("select_x"),
                options=df.columns.tolist(),
                default=st.session_state.x_columns,
                key="x_select",
            )
            st.session_state.x_columns = x_columns

        with col2:
            st.markdown(
                f'<p class="sub-section">{t("dependent_label")}</p>',
                unsafe_allow_html=True,
            )
            y_columns = st.multiselect(
                t("select_y"),
                options=df.columns.tolist(),
                default=st.session_state.y_columns,
                key="y_select",
            )
            st.session_state.y_columns = y_columns

        if len(x_columns) > 0 and len(y_columns) > 0:
            x_data = df[x_columns].copy()
            y_data = df[y_columns].copy()

            x_data = x_data.apply(pd.to_numeric, errors="coerce")
            y_data = y_data.apply(pd.to_numeric, errors="coerce")

            x_total = x_data.mean(axis=1)
            y_total = y_data.mean(axis=1)

            st.session_state.x_total = x_total
            st.session_state.y_total = y_total

            st.markdown(
                f'<div class="glass-badge-inline" style="display: inline-block; margin: 10px 0;">✅ {t("composite_success").format(nx=len(x_total.dropna()), ny=len(y_total.dropna()))}</div>',
                unsafe_allow_html=True,
            )

            # -------------------------------------------------
            # Section 3: Descriptive Statistics
            # -------------------------------------------------
            st.markdown(
                f'<p class="section-header">{t("descriptive_title")}</p>',
                unsafe_allow_html=True,
            )

            tab1, tab2 = st.tabs([t("variable_x_items"), t("variable_y_items")])

            with tab1:
                for col in x_columns:
                    st.markdown(
                        f'<div class="text-badge" style="font-weight: bold; font-size: 1.1rem;">{col}</div>',
                        unsafe_allow_html=True,
                    )
                    stats_dict, freq_df = compute_descriptive_stats(df[col], col)
                    if stats_dict:
                        c1, c2, c3, c4 = st.columns(4)
                        with c1:
                            st.metric("Mean", f"{stats_dict['Mean']:.4f}")
                        with c2:
                            st.metric("Median", f"{stats_dict['Median']:.4f}")
                        with c3:
                            st.metric("Std Dev", f"{stats_dict['Std Dev']:.4f}")
                        with c4:
                            st.metric("N", stats_dict["N"])

                        c5, c6, c7 = st.columns(3)
                        with c5:
                            st.metric("Min", f"{stats_dict['Minimum']:.2f}")
                        with c6:
                            st.metric("Max", f"{stats_dict['Maximum']:.2f}")
                        with c7:
                            st.metric("Mode", f"{stats_dict['Mode']:.2f}")

                        with st.expander(f"Frequency Table: {col}"):
                            st.dataframe(freq_df, use_container_width=True)

            with tab2:
                for col in y_columns:
                    st.markdown(
                        f'<div class="text-badge" style="font-weight: bold; font-size: 1.1rem;">{col}</div>',
                        unsafe_allow_html=True,
                    )
                    stats_dict, freq_df = compute_descriptive_stats(df[col], col)
                    if stats_dict:
                        c1, c2, c3, c4 = st.columns(4)
                        with c1:
                            st.metric("Mean", f"{stats_dict['Mean']:.4f}")
                        with c2:
                            st.metric("Median", f"{stats_dict['Median']:.4f}")
                        with c3:
                            st.metric("Std Dev", f"{stats_dict['Std Dev']:.4f}")
                        with c4:
                            st.metric("N", stats_dict["N"])

                        c5, c6, c7 = st.columns(3)
                        with c5:
                            st.metric("Min", f"{stats_dict['Minimum']:.2f}")
                        with c6:
                            st.metric("Max", f"{stats_dict['Maximum']:.2f}")
                        with c7:
                            st.metric("Mode", f"{stats_dict['Mode']:.2f}")

                        with st.expander(f"Frequency Table: {col}"):
                            st.dataframe(freq_df, use_container_width=True)

            # Composite scores stats
            st.markdown(
                f'<p class="sub-section">{t("composite_section")}</p>',
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    '<div class="text-badge" style="font-weight: bold; font-size: 1.1rem; margin-bottom: 10px;">X_total</div>',
                    unsafe_allow_html=True,
                )
                x_stats_dict, x_freq_df = compute_descriptive_stats(
                    x_total, "X_total"
                )
                if x_stats_dict:
                    st.metric("Mean", f"{x_stats_dict['Mean']:.4f}")
                    st.metric("Median", f"{x_stats_dict['Median']:.4f}")
                    st.metric("Mode", f"{x_stats_dict['Mode']:.4f}")
                    st.metric("Minimum", f"{x_stats_dict['Minimum']:.4f}")
                    st.metric("Maximum", f"{x_stats_dict['Maximum']:.4f}")
                    st.metric("Standard Deviation", f"{x_stats_dict['Std Dev']:.4f}")
                    st.metric("Variance", f"{x_stats_dict['Variance']:.4f}")
                    st.metric("N", x_stats_dict["N"])

                    with st.expander("Frequency Table: X_total"):
                        st.dataframe(x_freq_df, use_container_width=True)

            with col2:
                st.markdown(
                    '<div class="text-badge" style="font-weight: bold; font-size: 1.1rem; margin-bottom: 10px;">Y_total</div>',
                    unsafe_allow_html=True,
                )
                y_stats_dict, y_freq_df = compute_descriptive_stats(
                    y_total, "Y_total"
                )
                if y_stats_dict:
                    st.metric("Mean", f"{y_stats_dict['Mean']:.4f}")
                    st.metric("Median", f"{y_stats_dict['Median']:.4f}")
                    st.metric("Mode", f"{y_stats_dict['Mode']:.4f}")
                    st.metric("Minimum", f"{y_stats_dict['Minimum']:.4f}")
                    st.metric("Maximum", f"{y_stats_dict['Maximum']:.4f}")
                    st.metric("Standard Deviation", f"{y_stats_dict['Std Dev']:.4f}")
                    st.metric("Variance", f"{y_stats_dict['Variance']:.4f}")
                    st.metric("N", y_stats_dict["N"])

                    with st.expander("Frequency Table: Y_total"):
                        st.dataframe(y_freq_df, use_container_width=True)

            # -------------------------------------------------
            # Section 4: Visualizations
            # -------------------------------------------------
            st.markdown(
                f'<p class="section-header">{t("visual_title")}</p>',
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    f'<div class="text-badge" style="font-weight: bold; font-size: 1.1rem; margin-bottom: 10px;">{t("hist_x")}</div>',
                    unsafe_allow_html=True,
                )
                fig1, ax1 = plt.subplots(figsize=(8, 6))
                ax1.hist(
                    x_total.dropna(),
                    bins=20,
                    edgecolor="black",
                    alpha=0.7,
                    color="#60a5fa",
                )
                ax1.set_xlabel("X_total")
                ax1.set_ylabel("Frequency")
                ax1.set_title("Distribution of X_total")
                ax1.grid(True, alpha=0.3)
                st.pyplot(fig1)
                plt.close(fig1)

            with col2:
                st.markdown(
                    f'<div class="text-badge" style="font-weight: bold; font-size: 1.1rem; margin-bottom: 10px;">{t("hist_y")}</div>',
                    unsafe_allow_html=True,
                )
                fig2, ax2 = plt.subplots(figsize=(8, 6))
                ax2.hist(
                    y_total.dropna(),
                    bins=20,
                    edgecolor="black",
                    alpha=0.7,
                    color="#f97373",
                )
                ax2.set_xlabel("Y_total")
                ax2.set_ylabel("Frequency")
                ax2.set_title("Distribution of Y_total")
                ax2.grid(True, alpha=0.3)
                st.pyplot(fig2)
                plt.close(fig2)

            st.markdown(
                f'<div class="text-badge" style="font-weight: bold; font-size: 1.1rem; margin-bottom: 10px;">{t("boxplots")}</div>',
                unsafe_allow_html=True,
            )
            fig3, (ax3, ax4) = plt.subplots(1, 2, figsize=(12, 6))
            ax3.boxplot(x_total.dropna(), vert=True)
            ax3.set_ylabel("X_total")
            ax3.set_title("Boxplot: X_total")
            ax3.grid(True, alpha=0.3)

            ax4.boxplot(y_total.dropna(), vert=True)
            ax4.set_ylabel("Y_total")
            ax4.set_title("Boxplot: Y_total")
            ax4.grid(True, alpha=0.3)

            st.pyplot(fig3)
            plt.close(fig3)

            st.markdown(
                f'<div class="text-badge" style="font-weight: bold; font-size: 1.1rem; margin-bottom: 10px;">{t("scatter")}</div>',
                unsafe_allow_html=True,
            )
            fig4, ax5 = plt.subplots(figsize=(10, 6))
            valid_data = pd.DataFrame({"X": x_total, "Y": y_total}).dropna()
            ax5.scatter(valid_data["X"], valid_data["Y"], alpha=0.6, color="#22c55e")
            ax5.set_xlabel("X_total")
            ax5.set_ylabel("Y_total")
            ax5.set_title("Scatter Plot: X_total vs Y_total")
            ax5.grid(True, alpha=0.3)
            st.pyplot(fig4)
            plt.close(fig4)

            # -------------------------------------------------
            # Section 5: Association Analysis
            # -------------------------------------------------
            st.markdown(
                f'<p class="section-header">{t("association_title")}</p>',
                unsafe_allow_html=True,
            )

            valid_data = pd.DataFrame({"X": x_total, "Y": y_total}).dropna()

            if len(valid_data) > 2:
                st.markdown(
                    f'<p class="sub-section">{t("assumption_checks")}</p>',
                    unsafe_allow_html=True,
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(
                        f'<div class="text-badge" style="font-weight: bold; font-size: 1.1rem; margin-bottom: 10px;">{t("normality_x")}</div>',
                        unsafe_allow_html=True,
                    )
                    (
                        x_shapiro_stat,
                        x_shapiro_p,
                        x_normality_text,
                    ) = check_normality(x_total)
                    if x_shapiro_stat is not None:
                        st.metric("Shapiro-Wilk Statistic", f"{x_shapiro_stat:.4f}")
                        st.metric("p-value", f"{x_shapiro_p:.4f}")
                        st.markdown(
                            f'<div class="glass-badge-inline" style="display: inline-block; margin: 10px 0;">ℹ️ {x_normality_text}</div>',
                            unsafe_allow_html=True,
                        )

                with col2:
                    st.markdown(
                        f'<div class="text-badge" style="font-weight: bold; font-size: 1.1rem; margin-bottom: 10px;">{t("normality_y")}</div>',
                        unsafe_allow_html=True,
                    )
                    (
                        y_shapiro_stat,
                        y_shapiro_p,
                        y_normality_text,
                    ) = check_normality(y_total)
                    if y_shapiro_stat is not None:
                        st.metric("Shapiro-Wilk Statistic", f"{y_shapiro_stat:.4f}")
                        st.metric("p-value", f"{y_shapiro_p:.4f}")
                        st.markdown(
                            f'<div class="glass-badge-inline" style="display: inline-block; margin: 10px 0;">ℹ️ {y_normality_text}</div>',
                            unsafe_allow_html=True,
                        )

                if (x_shapiro_stat is not None) and (y_shapiro_stat is not None):
                    if (x_shapiro_p >= 0.05) and (y_shapiro_p >= 0.05):
                        recommended_method = "Pearson"
                        recommendation_text = t("reco_pearson")
                    else:
                        recommended_method = "Spearman"
                        recommendation_text = t("reco_spearman")
                else:
                    recommended_method = "Spearman"
                    recommendation_text = t("reco_spearman")

                st.markdown(
                    f'<div class="text-badge" style="font-weight: bold; font-size: 1.1rem; margin-bottom: 10px;">{t("recommendation_title")}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="glass-badge-inline" style="display: inline-block; margin: 10px 0;">💡 {recommendation_text}</div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f'<p class="sub-section">{t("corr_analysis")}</p>',
                    unsafe_allow_html=True,
                )

                method_choice = st.radio(
                    t("corr_choice"),
                    options=["Pearson", "Spearman"],
                    index=0 if recommended_method == "Pearson" else 1,
                    help=(
                        "Default mengikuti rekomendasi berdasarkan uji normalitas, "
                        "tetapi Anda tetap bisa memilih Pearson atau Spearman "
                        "secara manual."
                    ),
                )

                if method_choice == "Spearman":
                    correlation_r, correlation_p = stats.spearmanr(
                        valid_data["X"], valid_data["Y"]
                    )
                    corr_type = "Spearman"
                else:
                    correlation_r, correlation_p = stats.pearsonr(
                        valid_data["X"], valid_data["Y"]
                    )
                    corr_type = "Pearson"

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric(
                        f"{corr_type} Correlation (r)", f"{correlation_r:.4f}"
                    )
                with c2:
                    st.metric("p-value", f"{correlation_p:.4f}")
                with c3:
                    (
                        direction,
                        strength,
                        sig_text,
                        interpretation,
                    ) = interpret_correlation(correlation_r, correlation_p)
                    st.metric("Strength", strength.title())

                st.markdown(
                    '<div class="text-badge" style="font-weight: bold; font-size: 1.1rem; margin-bottom: 10px;">Interpretation:</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="glass-badge-inline" style="display: inline-block; margin: 10px 0;">📊 {interpretation}</div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    '<div class="text-badge" style="font-weight: bold; font-size: 1.1rem; margin-bottom: 10px;">Detailed Interpretation:</div>',
                    unsafe_allow_html=True,
                )
                interpretation_details = f"""
                <div class="glass-badge-inline" style="display: block; margin: 10px 0; padding: 16px;">
                <ul style="margin: 0; padding-left: 20px;">
                <li><strong>Jenis Korelasi yang Digunakan:</strong> {corr_type}</li>
                <li><strong>Correlation Coefficient (r):</strong> {correlation_r:.4f}</li>
                <li><strong>Direction:</strong> {direction.title()}</li>
                <li><strong>Strength:</strong> {strength.title()}</li>
                <li><strong>Statistical Significance:</strong> {sig_text}</li>
                <li><strong>Sample Size:</strong> {len(valid_data)}</li>
                </ul>
                </div>
                """
                st.markdown(interpretation_details, unsafe_allow_html=True)

                # -------------------------------------------------
                # Section 6: PDF Report Export
                # -------------------------------------------------
                st.markdown(
                    f'<p class="section-header">{t("pdf_title")}</p>',
                    unsafe_allow_html=True,
                )

                pdf_buffer = generate_pdf_report(
                    df,
                    x_columns,
                    y_columns,
                    x_total,
                    y_total,
                    x_stats_dict,
                    y_stats_dict,
                    x_freq_df,
                    y_freq_df,
                    correlation_r,
                    correlation_p,
                    interpretation,
                    x_normality_text
                    if "x_shapiro_stat" in locals() and x_shapiro_stat is not None else None,
                    y_normality_text
                    if "y_shapiro_stat" in locals() and y_shapiro_stat is not None else None,
                    lang_code,
                )

                st.download_button(
                    label=t("download_pdf"),
                    key="download_pdf",
                    data=pdf_buffer,
                    file_name="Statistics_Survey_Analysis_Report.pdf",
                    mime="application/pdf",
                )
            else:
                st.markdown(
                    f'<div class="glass-badge-inline" style="display: inline-block; margin: 10px 0;">⚠️ {t("insufficient_data")}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                f'<div class="glass-badge-inline" style="display: inline-block; margin: 10px 0;">⚠️ {t("select_warning")}</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            f'<div class="glass-badge-inline" style="display: inline-block; margin: 10px 0;">❌ {t("error_loading")}</div>',
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        f'<div class="glass-badge-inline" style="display: inline-block; margin: 10px 0; font-size: 1.1rem;">{t("upload_info")}</div>',
        unsafe_allow_html=True,
    )
