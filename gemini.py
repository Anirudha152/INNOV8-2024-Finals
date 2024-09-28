from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import os
import google.generativeai as genai
import fitz

printable = set(list(' ,`0123456789-=~!@#$%^&*()_+abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ,:;"\'/\n[]\\{}|?><.'))
bloat = {'per', 'and', 'but', 'the', 'for', 'are', 'was', 'were', 'be', 'been', 'with', 'you', 'this', 'but', 'his',
         'from', 'they', 'say', 'her', 'she', 'will', 'one', 'all', 'would', 'there', 'their', 'what', 'out', 'about',
         'who', 'get', 'which', 'when', 'make', 'can', 'like', 'time', 'just', 'into', 'year', 'your', 'good', 'some',
         'could', 'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
         'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because',
         'any', 'these', 'give', 'day', 'most'}
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

theta = SentenceTransformer("mixedbread-ai/mxbai-embed-large-v1")


def delimiter(phraset):
    l0=1
    for i in range(3):
        if phraset[i][1]>0.62:
            l0 += 1
    l1 = l0 + 1
    for i in range(10):
        if phraset[l0+i][1]>0.60:
            l1 += 1
    l2 = l1 + 1
    for i in range(20):
        if phraset[l1+i][1] >= 0.52:
            l2 += 1

    i1 = [x[0] for x in phraset[:l0]]
    i2 = [x[0] for x in phraset[l0:l1]]
    i3 = [x[0] for x in phraset[l1:l2]]
    return [i1, i2, i3]


def phrases_by_relevance(text, prompt):
    qembed = theta.encode([prompt])
    embeddings = theta.encode(text)
    result = [tensor.item() for tensor in list(cos_sim(qembed, embeddings)[0])]
    phraset = [(text[i], result[i]) for i in range(len(text))]
    phraset.sort(key=lambda x: x[1], reverse=True)
    return phraset


def cleaned(t):
    return "".join([i for i in t if i in printable])


def pdf_to_text(pdf):
    with fitz.open(pdf) as doc:
        ina = [cleaned(page.get_text()).split("\n") for page in doc]
        texta = []
        for a in ina:
            texta += a
        print("found text:", texta)
    return [k for k in texta if len(k)>2 and not k.isspace() and k not in bloat]


def process_pdf():
    context = pdf_to_text('Final_Resumes/Resume_of_ID_0.pdf')
    modified_pdf_files = []
    phraset = phrases_by_relevance(context, "Timeline")
    print('Passing these relevant texts to limiter:', phraset)
    classified = delimiter(phraset)
    print('importance order:', classified)
    print(phraset)


process_pdf()
# model = genai.GenerativeModel("gemini-1.5-flash")
# response = model.generate_content("Write a story about a magic backpack.")
# print(response.text)