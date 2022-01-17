import os
import io
import re
from tabulate import tabulate
import numpy as np
import nltk
nltk.downloader.Downloader()
from tika import parser
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import snowball


def text_preproc(x):
    """
    Preprocessing function

    Args:
        :param x: stringa su cui effettuare il preprocessing
        :return x: stringa

    """

    x = x.replace("xbd", " ").replace("xef", " ") \
        .replace("xbf", " ").replace(".", " ").replace(":", " ") \
        .replace("\\n", " ").replace("\\xc2\\xb7", " ").replace("\t", " ") \
        .replace("\\", " ").replace("\\xe2", " ") \
        .replace("\\x94", " ").replace("\\x80", " ")
    x = x.lower()  # all lowercase
    x = x.encode('ascii', 'ignore').decode()  # Encoding
    x = re.sub(r'https*\S+', ' ', x)  # Remove mentions
    x = re.sub(r'@\S+', ' ', x)  # Remove URL
    x = re.sub(r'#\S+', ' ', x)  # Remove Hashtags
    x = re.sub(r'\'\w+', '', x)  # Remove ticks and the next character
    x = re.sub(r'\w*\d+\w*', '', x)  # Remove numbers
    x = re.sub(r'\s{2,}', ' ', x)  # Replace the over spaces

    return x


def my_tokenizer(text):
    """
    Tokenization function (funzione che mi permette di eliminare stopwords e effettuare lo stemming)

        :param text: testo che deve essere tokenizzato
        :return pruned: lista di stringe

    """

    sw = stopwords.words('english')
    stemmer = snowball.SnowballStemmer(language="english")
    tokens = word_tokenize(text)
    pruned = [stemmer.stem(t.lower()) for t in tokens if re.search(r"^\w", t) and not t.lower() in sw]

    return pruned


def cos_similarity(input_query, dict_di_penta):
    """
    Funzione di cosine similarity fatta tra la query e i documenti

        :param input_query:  dizionario contenente come valore il titolo/titoli+abstract dei pdf dei revisori
        :param dict_di_penta: dizionario contenente come valore il titolo/titoli+abstract della query
        :return values:  dizionario contente come valore la lista dei valori di cos_similarity tra la query e i pdf dei revisori

    """

    texts = []
    values = {}

    for key in sorted(input_query.keys()):
        # Creates an array of tokenized documents
        texts.append(input_query[key])
    for pdf in sorted(dict_di_penta.keys()):
        vectorizer = CountVectorizer(tokenizer=my_tokenizer)
        # creates the model
        model = vectorizer.fit_transform(texts)
        # adds a query to the model
        query = vectorizer.transform([dict_di_penta[pdf]])
        cos = cosine_similarity(query, model)
        values.update({pdf: cos})

    return values


def jaccard_similarity(input_query_key, dict_keyword_di_penta):
    """
    Funzione di jaccard similarity tra la query e i singoli documenti

    :param input_query_key: dizionario contenente come valore le keywords dei pdf dei reviori
    :param dict_keyword_di_penta: dizionario contenente come valore le keywords dei pdf della query
    :return values_calculated: dizionario contenente come valore il massimo valore dello jaccard per ogni pdf query


    """
    values_keywords = []
    values_calculated = {}

    for file_pdf in sorted(dict_keyword_di_penta.keys()):
        for pfd_autore in sorted(input_query_key.keys()):
            # List the unique words in a document
            words_doc1 = set(input_query_key[pfd_autore].lower().replace(",", "").split())
            words_doc2 = set(dict_keyword_di_penta[file_pdf].lower().replace(",", "").split())

            # Find the intersection of words list of doc1 & doc2
            intersection = words_doc1.intersection(words_doc2)

            # Find the union of words list of doc1 & doc2
            union = words_doc1.union(words_doc2)

            # Calculate Jaccard similarity score
            # using length of intersection set divided by length of union set
            if not len(union) == 0:
                values_keywords.append((float(len(intersection)) / len(union)))
            else:
                values_keywords.append(0.0)
        massimo_keyword = float(np.mean(values_keywords))
        values_calculated.update({file_pdf: massimo_keyword})

    return values_calculated


if __name__ == '__main__':  # MAIN! ESTRAZIONE CONTENUTI PDF E VALUTAZIONE DELLA SOMIGLIANZA

    autori = []
    author_title_abstact = {}
    author_keywords = {}
    author_titles = {}

    path = "C:\\Users\\Donat\\Desktop\\PDFRidotti\\"

    # for per il prelievo di titolo abstract e keywords
    for file_PDF, sub_directory, files in os.walk(path, followlinks=True):
        for my_directory in sub_directory:
            title_abstract = {}
            keywords = {}
            titles = {}
            my_path = path + my_directory + "\\"
            author_name = my_directory
            for sub_filePDF, sub_dir, sub_files in os.walk(my_path, followlinks=True):
                for file_name in sub_files:

                    parsed_pdf = parser.from_file(my_path + file_name)
                    output = parsed_pdf['content']

                    with io.open('output.txt', 'w', encoding='utf8') as the_file:
                        if output:
                            the_file.write(str(output.lower().encode('utf8', errors='ignore')))

                    file_output = open("output.txt", "r", encoding="utf8").readline()
                    file_output = text_preproc(file_output)

                    try:
                        titl = re.findall('^.{0,120}', file_output)
                        titles[file_name] = titl[0]
                        if "abstract" in file_output[:1000]:
                            if "keywords" in file_output and not "index terms" in file_output:
                                abstr = re.findall('abstract(.*?)keywords', file_output)
                                title_abstract[file_name] = abstr[0] + titl[0]
                                keyw = re.findall('keywords(.*?)introduction', file_output)
                                keywords[file_name] = keyw[0]

                            elif "index terms" in file_output:
                                abstr = re.findall('abstract(.*?)index terms', file_output)
                                title_abstract[file_name] = abstr[0] + titl[0]
                                keyw = re.findall('index terms(.*?)introduction', file_output)
                                keywords[file_name] = keyw[0]

                            elif "introduction" in file_output:
                                abstr = re.findall('abstract(.*?)introduction', file_output)
                                title_abstract[file_name] = abstr[0] + titl[0]
                                keywords[file_name] = " "

                            else:
                                print("Non funziona")
                                print(file_name)

                        elif "summary" in file_output[:1000]:
                            if "keywords" in file_output and not "index terms" in file_output:
                                abstr = re.findall('summary(.*?)keywords', file_output)
                                title_abstract[file_name] = abstr[0] + titl[0]
                                keyw = re.findall('keywords(.*?)introduction', file_output)
                                keywords[file_name] = keyw[0]

                            elif "index terms" in file_output:
                                abstr = re.findall('summary(.*?)index terms', file_output)
                                title_abstract[file_name] = abstr[0] + titl[0]
                                keyw = re.findall('index terms(.*?)introduction', file_output)
                                keywords[file_name] = keyw[0]

                            elif "introduction" in file_output:
                                abstr = re.findall('summary(.*?)introduction', file_output)
                                title_abstract[file_name] = abstr[0] + titl[0]
                                keywords[file_name] = " "

                            else:
                                print("Non trova nulla")
                                print(file_name)

                        else:
                            abstr = re.findall('(.*?)introduction', file_output)
                            title_abstract[file_name] = abstr[0] + titl[0]
                            keywords[file_name] = " "

                    except:
                        print("Error in filename " + file_name + str(IOError))
                        continue

            author_title_abstact[author_name] = title_abstract
            author_keywords[author_name] = keywords
            author_titles[author_name] = titles
            autori.append(author_name)

    print("EXTRACTION ENDED SUCCESSFULLY")

    pdf_di_penta = []
    for pdf in sorted(author_titles["Massimiliano Di Penta"].keys()):
        pdf_di_penta.append(pdf)

    print("********************************")
    print()

    # 1) utilizzo della funzione jaccard per le KEYWORDS

    massimo_keywords = {}

    for nome_autore in sorted(author_keywords.keys()):
        if not "Massimiliano Di Penta" in nome_autore:
            valori_massimi = jaccard_similarity(author_keywords[nome_autore], author_keywords["Massimiliano Di Penta"])
            massimo_keywords.update({nome_autore: valori_massimi})

    autori_keywords = {}
    val_max_keywords_tabella = []

    for pdf in sorted(pdf_di_penta):
        print(pdf)
        for autore in sorted(autori):
            if not "Massimiliano Di Penta" in autore:
                print(autore + " -----> " + str(massimo_keywords[autore][pdf]))
                val_max_keywords_tabella.append(massimo_keywords[autore][pdf])
        autori_keywords.update({pdf: val_max_keywords_tabella})
        val_max_keywords_tabella = []
        print("<---------------------------------------------------->")

    print("********************************")
    print()

    # ROBERTO
    # 2) utilizzo della funzione cosine similarity sul TITOLO e ABSTRACT

    print("ABSTRACT+TITOLI")

    massimo_tit_ab = {}

    for nome_autore in sorted(author_title_abstact.keys()):
        if not "Massimiliano Di Penta" in nome_autore:
            valori_massimi = cos_similarity(author_title_abstact[nome_autore],
                                            author_title_abstact["Massimiliano Di Penta"])
            massimo_tit_ab.update({nome_autore: valori_massimi})

    autori_tit_ab = {}
    val_max_tit_ab_tabella = []

    for pdf in sorted(pdf_di_penta):
        print(pdf)
        for autore in sorted(autori):
            if not "Massimiliano Di Penta" in autore:
                print(autore + " -----> " + str(np.mean(massimo_tit_ab[autore][pdf])))
                val_max_tit_ab_tabella.append(float(np.mean(massimo_tit_ab[autore][pdf])))
        autori_tit_ab.update({pdf: val_max_tit_ab_tabella})
        val_max_tit_ab_tabella = []
        print("<---------------------------------------------------->")

    print("********************************")
    print()

    # 3) utilizzo della funzione cosine similarity sul TITOLO

    print("TITOLI")

    massimo_tit = {}

    for nome_autore in sorted(author_titles.keys()):
        if not "Massimiliano Di Penta" in nome_autore:
            valori_massimi = cos_similarity(author_titles[nome_autore], author_titles["Massimiliano Di Penta"])
            massimo_tit.update({nome_autore: valori_massimi})

    autori_titoli = {}
    val_max_tit_tabella = []

    for pdf in pdf_di_penta:
        print(pdf)
        for autore in sorted(autori):
            if not "Massimiliano Di Penta" in autore:
                print(autore + " -----> " + str(np.mean(massimo_tit[autore][pdf])))
                val_max_tit_tabella.append(float(np.mean(massimo_tit[autore][pdf])))
        autori_titoli.update({pdf: val_max_tit_tabella})
        val_max_tit_tabella = []
        print("<---------------------------------------------------->")

    autori.remove("Massimiliano Di Penta")

    for pdf in pdf_di_penta:
        info = {'Possibili Revisori': autori, 'Cosine Similarity: Titoli': autori_titoli[pdf],
                'Cosine Similarity: Titoli+Abstract': autori_tit_ab[pdf],
                'Jaccard Similarity: Keywords': autori_keywords[pdf]}
        print(tabulate(info, headers='keys', tablefmt='fancy_grid'))

    # for pdf in pdf_di_penta:
    #    crezioneTabella(pdf, autori, autori_titoli[pdf], autori_tit_ab[pdf], autori_keywords[pdf])
