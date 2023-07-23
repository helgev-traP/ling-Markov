import glob
import re
import MeCab

# 出現頻度の格納

transition_frequency = dict()
# transition_frequency["単語"][次に続く単語] == 頻度
transition_probability = dict()

# # wikiから遷移頻度を抽出

wiki_file_path_list = glob.glob("./wikipedia/doc/*/*")
wiki_file_nom = len(wiki_file_path_list)

for progress, wiki_file_path in enumerate(wiki_file_path_list):
    print("\b" * 20, end="", flush=True)
    print(progress, end="", flush=True)
    print("/", end="", flush=True)
    print(wiki_file_nom, end="", flush=True)
    with open(wiki_file_path) as f:
        wiki_file = f.read()

    # ## 行ごとに分割
    wiki_file_lines = wiki_file.split("\n")

    # ## 行ごとの処理
    for i in range(len(wiki_file_lines)):
        # セグフォ防止
        if wiki_file_lines[i] == "":
            continue
        # .で終わる行を削除
        if wiki_file_lines[i][len(wiki_file_lines[i]) - 1] == ".":
            wiki_file_lines[i] = ""
            continue
        # 行両端の＊を削除
        wiki_file_lines[i] = wiki_file_lines[i].strip("＊　")

    # 空行の削除
    for i in range(len(wiki_file_lines)):
        if wiki_file_lines[len(wiki_file_lines) - 1 - i] == "":
            wiki_file_lines.pop(len(wiki_file_lines) - 1 - i)

    # ## MeCabにぶち込む
    wiki_file_line_mecab = []
    # [行][単語][MeCab]
    tagger = MeCab.Tagger()
    for i in wiki_file_lines:
        line_mecab = tagger.parse(i)
        line_mecab_words = line_mecab.split("\n")

        # 行ごとの単語
        words = []
        for j in line_mecab_words:
            # 単語ごとのデータ
            mecab = j.split("\t")
            words.append(mecab)

        wiki_file_line_mecab.append(words)

    # ## 文ごとに分割する
    wiki_file_sentence_mecab = []
    # [文][単語][mecab]
    for i in wiki_file_line_mecab:
        sentence = []
        for j in i:
            sentence.append(j)
            if j[0] == "。":
                wiki_file_sentence_mecab.append(sentence)
                sentence = []

    # ## 遷移頻度を出す
    for sentence in wiki_file_sentence_mecab:
        for i in range(len(sentence)):
            if i != len(sentence) - 1:
                if sentence[i][0] not in transition_frequency:
                    transition_frequency[sentence[i][0]] = {sentence[i + 1][0]: 1}
                elif sentence[i + 1][0] not in transition_frequency[sentence[i][0]]:
                    transition_frequency[sentence[i][0]][sentence[i + 1][0]] = 1
                else:
                    transition_frequency[sentence[i][0]][sentence[i + 1][0]] += 1

# # 遷移頻度を確率に直す
