import tkinter as tk
from tkinter import scrolledtext

# 从文件中加载指定长度的单词列表
def load_words(filename, word_length):
    with open(filename, "r") as file:
        return [line.strip() for line in file if len(line.strip()) == word_length]

class WordleHelper:
    def __init__(self, root):
        self.root = root
        self.root.title("Wordle Helper")
        self.root.resizable(False, False)  # 设置窗口不可调整大小
        
        # 单词长度（默认5）
        self.word_length = tk.IntVar(value=5)
        self.words = []
        
        # 创建单词长度选择器
        tk.Label(root, text="单词长度:").grid(row=0, column=0, padx=5, pady=5)
        length_frame = tk.Frame(root)
        length_frame.grid(row=0, column=1, columnspan=6, padx=5, pady=5, sticky="w")
        tk.Radiobutton(length_frame, text="5字符", variable=self.word_length, value=5, command=self.change_word_length).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(length_frame, text="6字符", variable=self.word_length, value=6, command=self.change_word_length).pack(side=tk.LEFT, padx=5)
        
        # 存储输入框的引用
        self.known_letter_entries = []
        self.wrong_position_entries = []
        self.known_letters = []
        self.wrong_position_letters = []
        
        # 创建标签（只创建一次）
        self.known_label = tk.Label(root, text="已知字母:")
        self.known_label.grid(row=1, column=0, padx=5, pady=5)
        self.wrong_label = tk.Label(root, text="已知错误位置字母:")
        self.wrong_label.grid(row=2, column=0, padx=5, pady=5)
        
        # 初始化界面
        self.create_input_fields()
        
        # 创建不含字母输入区
        tk.Label(root, text="不含字母:").grid(row=3, column=0, padx=5, pady=5)
        self.excluded_letters = tk.StringVar()
        excluded_entry = tk.Entry(root, textvariable=self.excluded_letters)
        excluded_entry.grid(row=3, column=1, columnspan=6, padx=5, pady=5, sticky="ew")
        excluded_entry.bind("<KeyRelease>", self.update_guess_list)

        # 创建猜词列表
        tk.Label(root, text="猜词列表:").grid(row=4, column=0, padx=5, pady=5)
        self.guess_list = scrolledtext.ScrolledText(root, width=12, height=10)
        self.guess_list.grid(row=5, column=0, columnspan=3, padx=5, pady=5)

        # 创建尝试列表
        tk.Label(root, text="尝试列表:").grid(row=4, column=3, padx=5, pady=5)
        self.try_list = scrolledtext.ScrolledText(root, width=12, height=10)
        self.try_list.grid(row=5, column=3, columnspan=3, padx=5, pady=5)

        # 设置字体颜色标签
        self.guess_list.tag_configure("green", foreground="green")
        self.try_list.tag_configure("red", foreground="red")
        
        # 加载初始单词列表（必须在创建guess_list和try_list之后）
        self.load_word_list()

        # 创建清空按钮
        tk.Button(root, text="全部清空", command=self.clear_all).grid(row=6, column=0, columnspan=6, pady=5)
        
        # 配置列权重以便输入框可以扩展
        root.columnconfigure(1, weight=1)
    
    def create_input_fields(self):
        """创建已知字母和错误位置字母的输入框"""
        # 清除旧的输入框（如果存在）
        for entry in self.known_letter_entries:
            entry.destroy()
        for entry in self.wrong_position_entries:
            entry.destroy()
        
        self.known_letter_entries = []
        self.wrong_position_entries = []
        self.known_letters = [tk.StringVar() for _ in range(self.word_length.get())]
        self.wrong_position_letters = [tk.StringVar() for _ in range(self.word_length.get())]
        
        # 创建已知字母输入区
        for i in range(self.word_length.get()):
            entry = tk.Entry(self.root, textvariable=self.known_letters[i], width=2)
            entry.grid(row=1, column=i+1, padx=5, pady=5)
            entry.bind("<KeyRelease>", self.update_guess_list)
            self.known_letter_entries.append(entry)
        
        # 创建已知错误字母输入区
        for i in range(self.word_length.get()):
            entry = tk.Entry(self.root, textvariable=self.wrong_position_letters[i], width=2)
            entry.grid(row=2, column=i+1, padx=5, pady=5)
            entry.bind("<KeyRelease>", self.update_guess_list)
            self.wrong_position_entries.append(entry)
    
    def change_word_length(self):
        """当单词长度改变时重新创建界面并加载单词"""
        # 清空所有输入（但先检查输入框是否存在）
        if self.known_letters:
            for var in self.known_letters:
                var.set("")
        if self.excluded_letters:
            self.excluded_letters.set("")
        if self.wrong_position_letters:
            for var in self.wrong_position_letters:
                var.set("")
        self.guess_list.delete(1.0, tk.END)
        self.try_list.delete(1.0, tk.END)
        
        # 重新创建输入框
        self.create_input_fields()
        # 重新加载单词列表
        self.load_word_list()
        # 更新猜词列表
        self.update_guess_list()
    
    def load_word_list(self):
        """根据当前选择的长度加载单词列表"""
        self.words = load_words("words_alpha.txt", self.word_length.get())

    def update_guess_list(self, event=None):
        word_len = self.word_length.get()
        known_letters = [var.get() for var in self.known_letters]
        excluded_letters = self.excluded_letters.get()
        wrong_position_letters = [var.get() for var in self.wrong_position_letters]

        included_letters = ''.join(set(''.join(wrong_position_letters)))

        self.guess_list.delete(1.0, tk.END)  # 清空当前猜词列表

        filtered_words = []
        for word in self.words:
            match = True
            for i in range(word_len):
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
        for i in range(word_len):
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

        word_len = self.word_length.get()
        
        # 将已知字母从集合中移除
        known_letters_set = set(''.join(known_letters))

        # 从过滤后的单词中创建一个包含所有字母的集合
        all_letters = set(''.join(filtered_words))

        # 排除已知字母和已包含字母
        try_words = []
        for word in self.words:
            if any(letter in known_letters_set for letter in word):
                continue
            match = True
            for i in range(word_len):
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
        if self.known_letters:
            for var in self.known_letters:
                var.set("")
        if hasattr(self, 'excluded_letters'):
            self.excluded_letters.set("")
        if self.wrong_position_letters:
            for var in self.wrong_position_letters:
                var.set("")
        self.guess_list.delete(1.0, tk.END)
        self.try_list.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = WordleHelper(root)
    root.mainloop()
