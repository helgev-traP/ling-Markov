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
        # 階数(順方向)
        self.lorder = 0
        # 階数(逆方向)
        self.rorder = 0
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
        self.lorder = n
        self.rorder = n

    def set_lorder(self, n):
        self.lorder = n

    def det_rorder(self, n):
        self.rorder = n

    def add_frequency(self, sentences):
        if self.lorder <= 0:
            raise ValueError("set order")

        for s in sentences:
            n_gram = ["\\none"] * self.lorder
            for i in range(len(s)):
                # n_gramをひとつシフト
                n_gram.pop(0)
                n_gram.append(s[i][0])
                # transition_frequencyのキーにする空白区切りの語順を作る
                seq = n_gram[0]
                for j in range(1, self.lorder):
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

    def add_reverse_frequency(self, sentences):
        if self.rorder <= 0:
            raise ValueError("set order")

        for s in sentences:
            n_gram = ["\\none"] * self.lorder
            for i in range(len(s)):
                # n_gramをひとつシフト
                n_gram.pop(0)
                n_gram.append(s[i][0])
                # transition_frequencyのキーにする空白区切りの語順を作る
                seq = n_gram[0]
                for j in range(1, self.lorder):
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
        if self.lorder <= 0:
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
                    accu += self.transition_p[current_n_gram][j]
                    if accu > rund:
                        next_word = j
                        n_gram = current_n_gram.split(" ")
                        n_gram.pop(0)
                        n_gram.append(next_word)
                        next_n_gram = n_gram[0]
                        for k in range(1, self.lorder):
                            next_n_gram += " " + n_gram[k]
                        break
                if next_word == "。":
                    return next_word
                result = self.recursive(next_n_gram)
                if result != "\\faile":
                    return next_word + result
            return "\\faile"

    def generate(self, number_of_trials):
        if self.lorder <= 0:
            raise ValueError("set order")

        self.trial = number_of_trials
        current_n_gram = "\\none"
        for i in range(1, self.lorder):
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
                    first_word = j.split(" ")[self.lorder - 1]
                    n_gram = current_n_gram.split(" ")
                    n_gram.pop(0)
                    n_gram.append(first_word)
                    next_n_gram = n_gram[0]
                    for k in range(1, self.lorder):
                        next_n_gram += " " + n_gram[k]
                    break

            result = self.recursive(next_n_gram)
            if result != "\\faile":
                break

        return first_word + result

    def output(self, path):
        json = ""
        json += "{begin_p:"
        json += "{"
        for i in self.begin_p:
            json += '"' + i + '"' + ":" + str(self.begin_p[i]) + ","
        json += "}"
        json += "}"

        with open(path, mode="w") as f:
            f.write(json)


class Markov_random_n:
    def __init__(self) -> None:
        # 階数(順方向)
        self.lorder = 5
        # 階数(逆方向)
        self.rorder = 5
        # 最小階数
        self.min_order = 2
        # 試行回数
        self.trial = 10
        # 単語選択の閾値
        self.threshold = 0.0001
        # 遷移頻度
        # transition_frequency[階数]["語順(空白区切り)"][次に続く単語] == 頻度
        self.transition_f = dict()
        self.transition_rev_f = dict()
        # 遷移確率
        self.transition_p = dict()
        self.transition_rev_p = dict()

        # 文頭となる語とその頻度
        self.begin_f = dict()
        # 文頭となる語とその確率
        self.begin_p = dict()

    def set_order(self, n):
        self.set_lorder(n)
        self.set_rorder(n)

    def set_lorder(self, n):
        self.lorder = n
        for i in range(n):
            self.transition_f[i + 1] = dict()
            self.transition_p[i + 1] = dict()
            self.begin_f[i + 1] = dict()
            self.begin_p[i + 1] = dict()

    def set_rorder(self, n):
        self.rorder = n

    def set_min_order(self, n):
        self.min_order = n

    def add_frequency(self, sentences):
        if self.lorder <= 0:
            raise ValueError("set order")

        for o in range(1, self.lorder + 1):
            for s in sentences:
                n_gram = ["\\none"] * o
                for i in range(len(s)):
                    # n_gramをひとつシフト
                    n_gram.pop(0)
                    n_gram.append(s[i][0])
                    # transition_frequencyのキーにする空白区切りの語順を作る
                    seq = n_gram[0]
                    for j in range(1, o):
                        seq += " " + n_gram[j]
                    # 文頭となる頻度
                    if i == 0:
                        if seq not in self.begin_f[o]:
                            self.begin_f[o][seq] = 1
                        else:
                            self.begin_f[o][seq] += 1
                    # 遷移頻度
                    if i != len(s) - 1:
                        if seq not in self.transition_f[o]:
                            self.transition_f[o][seq] = {s[i + 1][0]: 1}
                        elif s[i + 1][0] not in self.transition_f[o][seq]:
                            self.transition_f[o][seq][s[i + 1][0]] = 1
                        else:
                            self.transition_f[o][seq][s[i + 1][0]] += 1

    def add_reverse_frequency(self, sentences):
        if self.rorder <= 0:
            raise ValueError("set order")

        for o in range(1, self.lorder + 1):
            for s in sentences:
                s_reversed = reversed(s)
                n_gram = ["\\none"] * o
                for i in range(len(s_reversed)):
                    # n_gramをひとつシフト
                    n_gram.pop(0)
                    n_gram.append(s_reversed[i][0])
                    # transition_frequencyのキーにする空白区切りの語順を作る
                    seq = n_gram[0]
                    for j in range(1, o):
                        seq += " " + n_gram[j]
                    # 文頭となる頻度
                    if i == 0:
                        if seq not in self.begin_f[o]:
                            self.begin_f[o][seq] = 1
                        else:
                            self.begin_f[o][seq] += 1
                    # 遷移頻度
                    if i != len(s_reversed) - 1:
                        if seq not in self.transition_rev_f[o]:
                            self.transition_rev_f[o][seq] = {s_reversed[i + 1][0]: 1}
                        elif s_reversed[i + 1][0] not in self.transition_rev_f[o][seq]:
                            self.transition_rev_f[o][seq][s_reversed[i + 1][0]] = 1
                        else:
                            self.transition_rev_f[o][seq][s_reversed[i + 1][0]] += 1

    def set_transition_probability(self):
        if self.lorder <= 0:
            raise ValueError("set order")

        # 文頭となる確率
        for o in range(1, self.lorder + 1):
            sum = 0
            for i in self.begin_f[o]:
                sum += self.begin_f[o][i]
            for i in self.begin_f[o]:
                self.begin_p[o][i] = self.begin_f[o][i] / sum

            # 遷移確率
            for i in self.transition_f[o]:
                sum = 0
                nextword_probability = dict()
                for j in self.transition_f[o][i]:
                    sum += self.transition_f[o][i][j]
                for j in self.transition_f[o][i]:
                    nextword_probability[j] = self.transition_f[o][i][j] / sum
                self.transition_p[o][i] = nextword_probability

    def set_reverse_transition_probability(self):
        if self.lorder <= 0:
            raise ValueError("set order")

        # 文頭となる確率
        for o in range(1, self.lorder + 1):
            sum = 0
            for i in self.begin_f[o]:
                sum += self.begin_f[o][i]
            for i in self.begin_f[o]:
                self.begin_p[o][i] = self.begin_f[o][i] / sum

            # 遷移確率
            for i in self.transition_rev_f[o]:
                sum = 0
                nextword_probability = dict()
                for j in self.transition_rev_f[o][i]:
                    sum += self.transition_rev_f[o][i][j]
                for j in self.transition_rev_f[o][i]:
                    nextword_probability[j] = self.transition_rev_f[o][i][j] / sum
                self.transition_rev_p[o][i] = nextword_probability

    def recursive(self, current_n_gram):
        # 階数を乱択
        order = random.randint(self.min_order, self.lorder)
        # print(current_n_gram)
        current_n_gram_split = current_n_gram.split(" ")
        order_n_gram = current_n_gram_split[self.lorder - order]
        for i in reversed(range(0, order - 1)):
            order_n_gram += " " + current_n_gram_split[self.lorder - i - 1]
        if order_n_gram not in self.transition_p[order]:
            return "\\faile"
        else:
            for i in range(self.trial):
                rund = random.random()
                accu = 0.0
                for j in self.transition_p[order][order_n_gram]:
                    accu += self.transition_p[order][order_n_gram][j]
                    if accu > rund and self.transition_p[order][order_n_gram][j] > self.threshold:
                        next_word = j
                        n_gram = order_n_gram.split(" ")
                        n_gram.pop(0)
                        n_gram.append(next_word)
                        next_n_gram = n_gram[0]
                        for k in range(1, order):
                            next_n_gram += " " + n_gram[k]
                        break
                if next_word == "。":
                    return next_word
                # next_n_gramをorder分の長さに整える
                for j in reversed(range(self.lorder - order)):
                    next_n_gram = current_n_gram_split[j + 1] + " " + next_n_gram
                result = self.recursive(next_n_gram)
                if result != "\\faile":
                    return next_word + result
            return "\\faile"

    def generate(self, number_of_trials):
        if self.lorder <= 0:
            raise ValueError("set order")

        self.trial = number_of_trials
        current_n_gram = "\\none"
        for i in range(1, self.lorder):
            current_n_gram += " " + "\\none"

        # 再帰的に文を生成する

        result = ""
        for i in range(self.trial):
            # 文頭を作る
            rund = random.random()
            accu = 0.0
            for j in self.begin_p[self.lorder]:
                accu += self.begin_p[self.lorder][j]
                if accu > rund:
                    first_word = j.split(" ")[self.lorder - 1]
                    n_gram = current_n_gram.split(" ")
                    n_gram.pop(0)
                    n_gram.append(first_word)
                    next_n_gram = n_gram[0]
                    for k in range(1, self.lorder):
                        next_n_gram += " " + n_gram[k]
                    break
            result = self.recursive(next_n_gram)
            if result != "\\faile":
                return first_word + result
        return result

    def output(self, path):
        json = ""
        json += "{begin_p:"
        json += "{"
        for i in self.begin_p:
            json += '"' + i + '"' + ":" + str(self.begin_p[i]) + ","
        json += "}"
        json += "}"

        with open(path, mode="w") as f:
            f.write(json)


# # wikiから遷移頻度を抽出

wiki_file_path_list = glob.glob("./wikipedia/doc/*/*")
wiki_file_nom = len(wiki_file_path_list)

markov_data = Markov_random_n()
markov_data.set_order(4)
limit = 5

# 読み込みの偏りを防ぐためwiki_file_path_listの内容をシャッフル
random.shuffle(wiki_file_path_list)
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

    # 文字種についての処理
    for i in range(len(wiki_file_lines)):
        # 空白の削除
        wiki_file_lines[i] = re.sub(" ", "", wiki_file_lines[i])
        # 鍵括弧の削除
        wiki_file_lines[i] = re.sub("「", "", wiki_file_lines[i])
        wiki_file_lines[i] = re.sub("」", "", wiki_file_lines[i])
        wiki_file_lines[i] = re.sub("『", "", wiki_file_lines[i])
        wiki_file_lines[i] = re.sub("』", "", wiki_file_lines[i])

    # 句点の有無を利用し見出しなどと思われるものを削除
    for i in range(len(wiki_file_lines)):
        if len(wiki_file_lines[i]) > 0:
            if wiki_file_lines[i][len(wiki_file_lines[i]) - 1] != "。":
                wiki_file_lines[i] = ""

    # 空行の削除
    wiki_file_lines_size = len(wiki_file_lines)
    for i in range(wiki_file_lines_size):
        if wiki_file_lines[wiki_file_lines_size - 1 - i] == "":
            wiki_file_lines.pop(wiki_file_lines_size - 1 - i)

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
for i in range(int(input("出力数"))):
    print(markov_data.generate(number_of_trials=10))
