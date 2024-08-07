import tkinter as tk
from tkinter import scrolledtext

# 从文件中加载5字符单词列表
def load_words(filename):
    with open(filename, "r") as file:
        return [line.strip() for line in file if len(line.strip()) == 5]

# 加载words_alpha.txt文件
words = load_words("words_alpha.txt")

class WordleHelper:
    def __init__(self, root):
        self.root = root
        self.root.title("Wordle Helper")
        self.root.resizable(False, False)  # 设置窗口不可调整大小

        # 创建已知字母输入区
        self.known_letters = [tk.StringVar() for _ in range(5)]
        tk.Label(root, text="已知字母:").grid(row=0, column=0, padx=5, pady=5)
        for i in range(5):
            entry = tk.Entry(root, textvariable=self.known_letters[i], width=2)
            entry.grid(row=0, column=i+1, padx=5, pady=5)
            entry.bind("<KeyRelease>", self.update_guess_list)

        # 创建不含字母输入区
        tk.Label(root, text="不含字母:").grid(row=1, column=0, padx=5, pady=5)
        self.excluded_letters = tk.StringVar()
        excluded_entry = tk.Entry(root, textvariable=self.excluded_letters)
        excluded_entry.grid(row=1, column=1, columnspan=5, padx=5, pady=5)
        excluded_entry.bind("<KeyRelease>", self.update_guess_list)

        # 创建已知错误字母输入区
        self.wrong_position_letters = [tk.StringVar() for _ in range(5)]
        tk.Label(root, text="已知错误位置字母:").grid(row=2, column=0, padx=5, pady=5)
        for i in range(5):
            entry = tk.Entry(root, textvariable=self.wrong_position_letters[i], width=2)
            entry.grid(row=2, column=i+1, padx=5, pady=5)
            entry.bind("<KeyRelease>", self.update_guess_list)

        # 创建猜词列表
        tk.Label(root, text="猜词列表:").grid(row=3, column=0, padx=5, pady=5)
        self.guess_list = scrolledtext.ScrolledText(root, width=12, height=10)
        self.guess_list.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

        # 创建尝试列表
        tk.Label(root, text="尝试列表:").grid(row=3, column=3, padx=5, pady=5)
        self.try_list = scrolledtext.ScrolledText(root, width=12, height=10)
        self.try_list.grid(row=4, column=3, columnspan=3, padx=5, pady=5)

        # 创建清空按钮
        tk.Button(root, text="全部清空", command=self.clear_all).grid(row=5, column=0, columnspan=6, pady=5)

        # 设置字体颜色标签
        self.guess_list.tag_configure("green", foreground="green")
        self.try_list.tag_configure("red", foreground="red")

    def update_guess_list(self, event=None):
        known_letters = [var.get() for var in self.known_letters]
        excluded_letters = self.excluded_letters.get()
        wrong_position_letters = [var.get() for var in self.wrong_position_letters]

        included_letters = ''.join(set(''.join(wrong_position_letters)))

        self.guess_list.delete(1.0, tk.END)  # 清空当前猜词列表

        filtered_words = []
        for word in words:
            match = True
            for i in range(5):
                if known_letters[i] and known_letters[i] != word[i]:
                    match = False
                    break
            if not match:
                continue
            if not all(letter in word for letter in included_letters):
                continue
            if any(letter in word for letter in excluded_letters):
                continue
            if any(wrong_letters and word[i] in wrong_letters for i, wrong_letters in enumerate(wrong_position_letters)):
                continue
            filtered_words.append(word)

        # 检查每个位置的字母是否相同，并自动补充到已知字母里
        for i in range(5):
            if known_letters[i]:
                continue
            same_letter = set(word[i] for word in filtered_words)
            if len(same_letter) == 1:
                self.known_letters[i].set(same_letter.pop())

        # 按单词中不同字母的数量进行排序
        filtered_words.sort(key=lambda x: len(set(x)), reverse=True)

        for word in filtered_words:
            for i, letter in enumerate(word):
                if known_letters[i] == letter:
                    self.guess_list.insert(tk.END, letter, "green")
                else:
                    self.guess_list.insert(tk.END, letter)
            self.guess_list.insert(tk.END, "\n")

        self.update_try_list(filtered_words, known_letters, wrong_position_letters)

    def update_try_list(self, filtered_words, known_letters, wrong_position_letters):
        self.try_list.delete(1.0, tk.END)  # 清空当前尝试列表

        # 将已知字母从集合中移除
        known_letters_set = set(''.join(known_letters))

        # 从过滤后的单词中创建一个包含所有字母的集合
        all_letters = set(''.join(filtered_words))

        # 排除已知字母和已包含字母
        try_words = []
        for word in words:
            if any(letter in known_letters_set for letter in word):
                continue
            match = True
            for i in range(5):
                if wrong_position_letters[i] and word[i] in wrong_position_letters[i]:
                    match = False
                    break
            if not match:
                continue

            # 检查是否包含至少3个猜词列表中的字母
            common_letters = len(set(word).intersection(all_letters))
            if common_letters >= 3:
                try_words.append(word)

        # 按单词中不同字母的数量进行排序
        try_words.sort(key=lambda x: len(set(x).intersection(all_letters)), reverse=True)

        for word in try_words:
            for letter in word:
                if letter in all_letters:
                    self.try_list.insert(tk.END, letter, "red")
                else:
                    self.try_list.insert(tk.END, letter)
            self.try_list.insert(tk.END, "\n")

    def clear_all(self):
        for var in self.known_letters:
            var.set("")
        self.excluded_letters.set("")
        for var in self.wrong_position_letters:
            var.set("")
        self.guess_list.delete(1.0, tk.END)
        self.try_list.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = WordleHelper(root)
    root.mainloop()
