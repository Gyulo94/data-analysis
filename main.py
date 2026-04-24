import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==============================================================
# 한글 폰트 및 기본 설정
# ==============================================================
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# ==============================================================
# 1. 데이터 로드 및 전처리
# ==============================================================
df = pd.read_csv('data/global_ai_workforce_automation_2015_2025.csv')
df['Net_Job_Impact'] = df['Job_Creation_Million'] - df['Job_Displacement_Million']

print(f"국가 수: {df['Country'].nunique()}개 | 기간: {df['Year'].min()}~{df['Year'].max()}")

# ==============================================================
# 2. 국가명 한국어 매핑
# ==============================================================
country_map = {
    'United States': '미국', 'China': '중국', 'Germany': '독일', 'Japan': '일본',
    'South Korea': '대한민국', 'United Kingdom': '영국', 'France': '프랑스', 'India': '인도',
    'Brazil': '브라질', 'Canada': '캐나다', 'Australia': '호주', 'Russia': '러시아',
    'Netherlands': '네덜란드', 'Sweden': '스웨덴', 'Turkey': '터키', 'Singapore': '싱가포르',
    'Spain': '스페인', 'Italy': '이탈리아', 'South Africa': '남아프리카', 'Mexico': '멕시코'
}

# ==============================================================
# 3. 한국어 레이블 매핑
# ==============================================================
label_map = {
    'AI_Investment_BillionUSD': 'AI 투자액 (억 달러)',
    'Automation_Rate_Percent': '자동화율 (%)',
    'Employment_Rate_Percent': '고용률 (%)',
    'Net_Job_Impact': '순 일자리 영향 (백만 명)',
    'Reskilling_Investment_MillionUSD': '재교육 투자 (백만 달러)',
    'AI_Readiness_Score': 'AI 준비도 점수',
}

# ==============================================================
# 4. 가설별 회귀 시각화
# ==============================================================

for h_num, (title, x_col, y_col, color) in enumerate([
    ('H1: 자동화율이 올라가면 고용률이 정말 줄어들까?', 'Automation_Rate_Percent', 'Employment_Rate_Percent', 'red'),
    ('H2: AI에 돈 많이 쓰면 일자리가 정말 줄어들까?', 'AI_Investment_BillionUSD', 'Net_Job_Impact', 'blue'),
    ('H3: 자동화율이 높아지면 일자리가 정말 줄어들까?', 'Automation_Rate_Percent', 'Net_Job_Impact', 'purple'),
    ('H4: 재교육에 투자하면 AI가 뺏은 일자리를 되살릴 수 있을까?', 'Reskilling_Investment_MillionUSD', 'Net_Job_Impact', 'green'),
    ('H5: AI 준비도가 높은 나라는 자동화 충격을 버틸 수 있을까?', 'AI_Readiness_Score', 'Net_Job_Impact', 'orange')
], 1):
    plt.figure(figsize=(12, 7))
    sns.regplot(data=df, x=x_col, y=y_col, scatter_kws={'alpha':0.6}, line_kws={'color':color}, ci=None)
    plt.title(title, fontsize=15)
    plt.xlabel(label_map.get(x_col, x_col))
    plt.ylabel(label_map.get(y_col, y_col))
    if y_col == 'Net_Job_Impact':
        plt.axhline(y=0, color='gray', linestyle='--')
    plt.tight_layout()
    plt.savefig(f'0{h_num}_h{h_num}_{x_col.split("_")[0].lower()}_vs_netjob.png', dpi=200, bbox_inches='tight')
    plt.show()

# ==============================================================
# 5. 국가별 순 일자리 영향 비교 (국가명 한국어 적용)
# ==============================================================
df['Country_KR'] = df['Country'].map(country_map).fillna(df['Country'])

country_net = df.groupby('Country_KR')['Net_Job_Impact'].mean().sort_values(ascending=False)

korea_value = country_net.get('대한민국', None)
if korea_value is not None:
    korea_rank = country_net.rank(ascending=False)['대한민국']

plt.figure(figsize=(15, 11))

top15 = country_net.head(15)
bottom10 = country_net.tail(10)
selected = pd.concat([top15, bottom10]).drop_duplicates()
selected = selected.sort_values(ascending=True)

colors = []
for country, val in selected.items():
    if country == '대한민국':
        colors.append('#2E86C1')
    elif val > 0:
        colors.append('#28B463')
    else:
        colors.append('#E74C3C')

bars = plt.barh(selected.index, selected.values, color=colors, alpha=0.85)
max_value = selected.max()
for bar in bars:
    width = bar.get_width()
    y = bar.get_y() + bar.get_height()/2
    
    if width > 0:
        x_pos = width - 0.15 * abs(width)
        ha = 'right'
        color = 'white'
        fontweight = 'bold'
    else:   
        x_pos = width - 0.02 * abs(width)
        ha = 'right'
        color = 'black'
        fontweight = 'bold'
    
    plt.text(x_pos, y, f'{width:.2f}', 
             va='center', ha=ha, fontsize=10.5, 
             fontweight=fontweight, color=color)
    
plt.title('국가별 평균 순 일자리 영향 (2015~2025)\n(양수 = AI로 일자리 증가, 음수 = AI로 일자리 감소)', 
          fontsize=16, pad=25)
plt.xlabel('평균 순 일자리 영향 (백만 명)')
plt.ylabel('국가')
plt.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('06_country_net_job_impact.png', dpi=200, bbox_inches='tight')
plt.show()

# ==============================================================
# 6. 최종 결론
# ==============================================================
print(f"\n전체 평균 순 일자리 영향: {df['Net_Job_Impact'].mean():.3f} 백만 명")
print(f"대한민국: {korea_value:.3f} 백만 명")