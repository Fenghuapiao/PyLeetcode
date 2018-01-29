import os
import glob
import json
import time
import requests as rq

class Config:
    leetcode_url = 'https://leetcode.com/problems/'
    local_path = './LeetcodeAlgorithms/'
    github_url = 'https://github.com/Fenghuapiao/PyLeetcode/blob/master'

class Question:
    """
    this class used to store the inform of every question
    """
    def __init__(self, id_,
                 name, url,
                 lock, difficulty):
        self.id_ = id_
        self.title = name
        # the problem description url　问题描述页
        self.url = url
        self.lock = lock  # boolean，锁住了表示需要购买
        self.difficulty = difficulty
        # the solution url
        self.python = ''

class CompleteInform:
    """
    this is statistic inform
    """

    def __init__(self):
        self.solved = {
            'python': 0,
        }
        self.complete_num = 0
        self.lock = 0
        self.total = 0

    def __repr__(self):
        return str(self.solved)

class Readme:
    """
    generate folder and markdown file
    update README.md when you finish one problem by some language
    """

    def __init__(self, total, solved, locked, others=None):
        """
        :param total: total problems nums
        :param solved: solved problem nums
        """
        self.total = total
        self.solved = solved
        self.others = others
        self.locked = locked
        self.time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.msg = '# Cease to struggle and you cease to live!\n' \
                   'Until {}, I have solved **{}** / **{}** problems ' \
                   'while **{}** are still locked.' \
                   '\n\nCompletion statistic: ' \
                   '\nPython: {python}' \
                   '\n\nNote: :lock: means you need to buy a book from LeetCode\n'.format(
                    self.time, self.solved, self.total, self.locked, **self.others)

    def create_leetcode_readme(self, table_instance):
        """
        create REAdME.md
        :return:
        """
        file_path = './README.md'
        # write some basic inform about leetcode
        with open(file_path, 'w') as f:
            f.write(self.msg)
            f.write('\n----------------\n')

        with open(file_path, 'a') as f:
            f.write('## LeetCode Solution Table\n')
            f.write('| ID | Title | Difficulty | Python |\n')
            f.write('|:---:' * 4 + '|\n')
            table, table_item = table_instance
            for index in table:
                item = table_item[index]
                if item.lock:
                    _lock = ':lock:'
                else:
                    _lock = ''
                data = {
                    'id': item.id_,
                    'title': '[{}]({}) {}'.format(item.title, item.url, _lock),
                    'difficulty': item.difficulty,
                    'python': item.python if item.python else 'To Do',
                }
                line = '|{id}|{title}|{difficulty}|{python}|\n'.format(**data)
                f.write(line)
            print('README.md was created.....')

class TableInform:
    def __init__(self):
        # raw questions inform
        self.questions = []
        # this is table index
        self.table = []
        # this is the element of question
        self.table_item = {}
        self.locked = 0

    def get_leetcode_problems(self):
        """
        used to get leetcode inform
        :return:
        """
        # we should look the response data carefully to find law
        # return byte. content type is byte
        content = rq.get('https://leetcode.com/api/problems/algorithms/').text
        # get all problems
        self.questions = json.loads(content)['stat_status_pairs']
        # print(self.questions)
        difficultys = ['Easy', 'Medium', 'Hard']
        for i in range(len(self.questions) - 1, -1, -1):
            question = self.questions[i]
            name = question['stat']['question__title']
            url = question['stat']['question__title_slug']
            id_ = str(question['stat']['frontend_question_id'])
            if int(id_) < 10:
                id_ = '00' + id_
            elif int(id_) < 100:
                id_ = '0' + id_
            lock = question['paid_only']
            if lock:
                self.locked += 1
            difficulty = difficultys[question['difficulty']['level'] - 1]
            url = Config.leetcode_url + url + '/description/'
            q = Question(id_, name, url, lock, difficulty)
            self.table.append(q.id_)
            self.table_item[q.id_] = q
        return self.table, self.table_item
    def create_folder(self):
        oj_algorithms = Config.local_path
        self.get_leetcode_problems()
        if os.path.exists(oj_algorithms):
            print(' algorithms is already exits')
        else:
            print('creating {} algorithms....')
            os.mkdir(oj_algorithms)
        for item in self.table_item.values():
            question_folder_name = oj_algorithms + item.id_ + '. ' + item.title
            if not os.path.exists(question_folder_name):
                print(question_folder_name + 'is not exits, create it now....')
                os.mkdir(question_folder_name)

    def update_table(self):
        # the complete inform should be update
        complete_info = CompleteInform()
        self.get_leetcode_problems()
        # the total problem nums
        # complete_info.total = len(self.table)
        # complete_info.lock = self.locked
        complete_info = CompleteInform()
        # count = 0
        for i in glob.glob(Config.local_path + '*'):
            for j in glob.glob(i + '/*'):
                if j.endswith('.py'):
                    complete_info.solved['python'] += 1
                    # count += 1
                    folder_url = j
                    self.table_item[i[21:24]].python = '[Python]({})'.format((Config.github_url+j[1:]).replace(' ', '%20'))
        readme = Readme(len(self.table),
                        complete_info.solved,
                        self.locked,
                        complete_info.solved)
        readme.create_leetcode_readme([self.table, self.table_item])

def main():
    table = TableInform()
    table.update_table()
if __name__ == '__main__':
    main()
