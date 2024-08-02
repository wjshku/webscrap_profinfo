from profinfo_byuni import *
from analysis import list_sum_unique_elements, filter_for_listofstrings, \
                    find_embedding_matrix, get_cor_withembedmatrix

nus_professors = nus_profs()
# nus_professors.get_prof_basicinfo()
# nus_professors.store_prof_info('basic')
nus_professors.read_prof_info('basic')

prof_df = nus_professors.basicinfo

# Get All Research Area
research_areas = list_sum_unique_elements(prof_df['ResearchArea'])

# Number of Prof by Title
print(prof_df.groupby('Title').count()['Name'])

text = 'Applied Machine Learning'
ri_matrix = find_embedding_matrix(sentences=research_areas,index_names=research_areas)
most_relatedri = get_cor_withembedmatrix(text,ri_matrix).sort_values(ascending=False).head()
print(f'Most Related Research Interests with {text} Found:')
print(most_relatedri)

prof_researchinterests = prof_df['ResearchArea'].apply(filter_for_listofstrings,texts=most_relatedri.index)
print('Professors with the Relevant RI:')
print(prof_df[prof_researchinterests==True][['Name','Title','Bio']])