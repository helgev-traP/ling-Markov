"""
ライブラリとして、
mecab-python3 1.0.6
unidic-lite   1.0.8
を使用。
"""
import glob
import re
import MeCab
import random

# # 出現頻度の格納


class Markov_1:
    def __init__(self) -> None:
        # 遷移頻度
        # transition_frequency["単語"][次に続く単語] == 頻度
        self.transition_f = dict()
        # 遷移確率
        self.transition_p = dict()
        # 文頭となる語とその頻度
        self.begin_f = dict()
        # 文頭となる語とその確率
        self.begin_p = dict()

    def add_frequency(self, sentences):
        for s in sentences:
            for i in range(len(s)):
                # 文頭となる頻度
                if i == 0:
                    if s[i][0] not in self.begin_f:
                        self.begin_f[s[i][0]] = 1
                    else:
                        self.begin_f[s[i][0]] += 1
                # 遷移頻度
                if i != len(s) - 1:
                    if s[i][0] not in self.transition_f:
                        self.transition_f[s[i][0]] = {s[i + 1][0]: 1}
                    elif s[i + 1][0] not in self.transition_f[s[i][0]]:
                        self.transition_f[s[i][0]][s[i + 1][0]] = 1
                    else:
                        self.transition_f[s[i][0]][s[i + 1][0]] += 1

    def set_transition_probability(self):
        # 文頭となる確率
        sum = 0
        for i in self.begin_f:
            sum += self.begin_f[i]
        for i in self.begin_f:
            self.begin_p[i] = self.begin_f[i] / sum

        # 遷移確率
        for i in self.transition_f:
            sum = 0
            nextword_probability = dict()
            for j in self.transition_f[i]:
                sum += self.transition_f[i][j]
            for j in self.transition_f[i]:
                nextword_probability[j] = self.transition_f[i][j] / sum
            self.transition_p[i] = nextword_probability

    def generate(self, size):
        current_word = "。"
        l = 1

        while True:
            rund = random.random()
            accu = 0.0
            if current_word == "。":
                for i in self.begin_p:
                    accu += self.begin_p[i]
                    if accu > rund:
                        print(i, end="")
                        current_word = i
                        break
            else:
                for i in self.transition_p[current_word]:
                    accu += self.transition_p[current_word][i]
                    if accu > rund:
                        print(i, end="")
                        current_word = i
                        break
                l += 1
                if current_word == "。":
                    break
            if l > size:
                break


class Markov_n:
    def __init__(self) -> None:
        # 階数
        self.order = 0
        # 試行回数
        self.trial = 0
        # 遷移頻度
        # transition_frequency["語順(空白区切り)"][次に続く単語] == 頻度
        self.transition_f = dict()
        # 遷移確率
        self.transition_p = dict()
        # 文頭となる語とその頻度
        self.begin_f = dict()
        # 文頭となる語とその確率
        self.begin_p = dict()

    def set_order(self, n):
        self.order = n

    def add_frequency(self, sentences):
        if self.order <= 0:
            raise ValueError("set order")

        for s in sentences:
            n_gram = ["\\none"] * self.order
            for i in range(len(s)):
                # n_gramをひとつシフト
                n_gram.pop(0)
                n_gram.append(s[i][0])
                # transition_frequencyのキーにする空白区切りの語順を作る
                seq = n_gram[0]
                for j in range(1, self.order):
                    seq += " " + n_gram[j]
                # 文頭となる頻度
                if i == 0:
                    if seq not in self.begin_f:
                        self.begin_f[seq] = 1
                    else:
                        self.begin_f[seq] += 1
                # 遷移頻度
                if i != len(s) - 1:
                    if seq not in self.transition_f:
                        self.transition_f[seq] = {s[i + 1][0]: 1}
                    elif s[i + 1][0] not in self.transition_f[seq]:
                        self.transition_f[seq][s[i + 1][0]] = 1
                    else:
                        self.transition_f[seq][s[i + 1][0]] += 1

    def set_transition_probability(self):
        if self.order <= 0:
            raise ValueError("set order")

        # 文頭となる確率
        sum = 0
        for i in self.begin_f:
            sum += self.begin_f[i]
        for i in self.begin_f:
            self.begin_p[i] = self.begin_f[i] / sum

        # 遷移確率
        for i in self.transition_f:
            sum = 0
            nextword_probability = dict()
            for j in self.transition_f[i]:
                sum += self.transition_f[i][j]
            for j in self.transition_f[i]:
                nextword_probability[j] = self.transition_f[i][j] / sum
            self.transition_p[i] = nextword_probability

    def recursive(self, current_n_gram):
        if current_n_gram not in self.transition_p:
            return "\\faile"
        else:
            for i in range(self.trial):
                rund = random.random()
                accu = 0.0
                for j in self.transition_p[current_n_gram]:
                    accu += self.transition_p[j]
                    if accu > rund:
                        next_word = j.split(" ")[self.order - 1]
                        n_gram = current_n_gram.split(" ")
                        n_gram.pop(0)
                        n_gram.append(next_word)
                        next_n_gram = n_gram[0]
                        for k in range(1, self.order):
                            next_n_gram += " " + n_gram[k]
                        break
                if next_word == "。":
                    return next_word
                result = self.generate(next_n_gram)
                if result != "\\faile":
                    return next_word + result
            return "\\faile"

    def generate(self, number_of_trials):
        if self.order <= 0:
            raise ValueError("set order")

        self.trial = number_of_trials
        current_n_gram = "\\none"
        for i in range(1, self.order):
            current_n_gram += " " + "\\none"

        # 再帰的に文を生成する

        result = ""
        for i in range(self.trial):
            # 文頭を作る
            rund = random.random()
            accu = 0.0
            for j in self.begin_p:
                accu += self.begin_p[j]
                if accu > rund:
                    first_word = j.split(" ")[self.order - 1]
                    n_gram = current_n_gram.split(" ")
                    n_gram.pop(0)
                    n_gram.append(first_word)
                    next_n_gram = n_gram[0]
                    for k in range(1, self.order):
                        next_n_gram += " " + n_gram[k]
                    break

            result = self.recursive(next_n_gram)
            if result != "\\faile":
                break

        return first_word + result


# # wikiから遷移頻度を抽出

wiki_file_path_list = glob.glob("./wikipedia/doc/*/*")
wiki_file_nom = len(wiki_file_path_list)

markov_data = Markov_n()
markov_data.set_order(3)
limit = 1
print("wiki読み込み\n進捗\t/ 設定上限\t/ 全データページ数")
for progress, wiki_file_path in enumerate(wiki_file_path_list):
    if progress >= limit:
        break
    print("\b" * 30, end="", flush=True)
    print(progress, end="", flush=True)
    print("\t/ ", end="", flush=True)
    print(limit, end="", flush=True)
    print("\t/ ", end="", flush=True)
    print(wiki_file_nom, end="", flush=True)
    with open(wiki_file_path) as f:
        wiki_file = f.read()

    # ## 行ごとに分割
    wiki_file_lines = wiki_file.split("\n")

    # ## 行ごとの処理
    for i in range(len(wiki_file_lines)):
        # セグメンテーションフォルト防止
        if wiki_file_lines[i] == "":
            continue
        # .で終わる行を削除
        if wiki_file_lines[i][len(wiki_file_lines[i]) - 1] == ".":
            wiki_file_lines[i] = ""
            continue
        # 行両端の＊を削除
        wiki_file_lines[i] = wiki_file_lines[i].strip("＊　")

    # 空行の削除
    wiki_file_lines_size = len(wiki_file_lines)
    for i in range(wiki_file_lines_size):
        if wiki_file_lines[wiki_file_lines_size - 1 - i] == "":
            wiki_file_lines.pop(wiki_file_lines_size - 1 - i)

    # 文字種についての処理
    for i in range(len(wiki_file_lines)):
        # 空白の削除
        wiki_file_lines[i] = re.sub(" ", "", wiki_file_lines[i])
        # 鍵括弧の削除
        wiki_file_lines[i] = re.sub("「", "", wiki_file_lines[i])
        wiki_file_lines[i] = re.sub("」", "", wiki_file_lines[i])

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
    markov_data.add_frequency(wiki_file_sentence_mecab)
print()

# # 遷移頻度を確率に直す
markov_data.set_transition_probability()

# # 出力
print(markov_data.generate(number_of_trials=5))
