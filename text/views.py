from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt

import json
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx


def read_article(file_content):
    article = file_content.split('. ')
    sentences = []
    for sentence in article:
        sentences.append(sentence.replace("[^a-zA-Z]", "").split(" "))
    if sentences[-1] == ['']:
        sentences.pop()  # Remove the last element if it's empty
    return sentences

def sentence_similarity(sen1, sen2, stopwords=None):
    if stopwords is None:
        stopwords = []
    sen1 = [w.lower() for w in sen1 if w not in stopwords]
    sen2 = [w.lower() for w in sen2 if w not in stopwords]

    all_words = list(set(sen1 + sen2))

    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    for w in sen1:
        vector1[all_words.index(w)] += 1
    for w in sen2:
        vector2[all_words.index(w)] += 1

    return 1 - cosine_distance(vector1, vector2)

def gen_sim_matrix(sentences, stop_words):
    similarity_matrix = np.zeros((len(sentences), len(sentences)))
    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2:
                continue
            similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)
    return similarity_matrix

def generate_summary(file_content, top_n=5):
    stop_words = stopwords.words('english')
    summarize_text = []

    sentences = read_article(file_content)
    if not sentences:
        return "The file is empty or does not contain valid sentences."

    sentence_similarity_matrix = gen_sim_matrix(sentences, stop_words)

    # Convert similarity matrix to a graph
    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_matrix)

    # Rank sentences using PageRank
    scores = nx.pagerank(sentence_similarity_graph)

    # Sort the sentences by score
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)

    # Select the top N sentences
    for i in range(top_n):
        summarize_text.append(" ".join(ranked_sentences[i][1]))

    return ". ".join(summarize_text)

def text(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render())

def summarize(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        file_conntent = data.get('text', '')
        summary = generate_summary(file_conntent, top_n=2)
        return JsonResponse({'summary' : summary})
    return JsonResponse({'error' :'invalid request method'},status=400)