# -*- coding: utf-8 -*-

import os
from random import choice, random, randint

CHANCE_OF_BROKEN_COMMIT = 0.1


def shell(cmd):
    exitcode = os.system(cmd)
    if exitcode != 0:
        raise RuntimeWarning(f'command exited with exitcode {exitcode}: \n {cmd}')


class CommitContentProvider:
    def __init__(self, top):
        self.pool = set(range(1, top + 1))  # эти числа по одному попадут в файл
        self.content = []  # содержимое файла для коммитов (список строк)
        self.commit_n = 0  # номер коммита
        
    def prepare_content(self):
        next_from_pool = choice(list(self.pool))
        self.pool.remove(next_from_pool)

        value = '%03d' % next_from_pool
        insert_pos = randint(0, len(self.content))
        self.content.insert(insert_pos, value)
        
        self.commit_n += 1
        
        return self.content

    def get_content_for_commit(self):
        lines = self.prepare_content()
        if len(self.pool) > 1 and random() < CHANCE_OF_BROKEN_COMMIT:
            sep = ''
            header = 'Это сломанный коммит № %d, в котором что-то сделано, но нельзя понять, что именно.'
        else:
            sep = '\n'
            header = 'Это нормальный коммит № %d, в котором можно найти искомое число.'
            
        return (header % self.commit_n) + '\n\n' + (sep.join(lines)) + '\n'
        
    def generate_commits(self):
        while self.pool:
            yield self.get_content_for_commit()



def make_repo_for_bisect(repo_name, commit_count=100, target_file_name='file.txt'):
    # создать папку и пустой репозиторий в ней
    os.system(f'mkdir {repo_name}')
    os.chdir(f'{repo_name}')
    os.system('git init')
    
    ccp = CommitContentProvider(commit_count)

    for i, content in enumerate(ccp.generate_commits()):
        with open(target_file_name, 'w') as f:
            f.write(content)

        if i < 2:
            shell(f'git add {target_file_name}')
        shell(f'git commit -a -m "commit-{i + 1}"')

        if i % 10 == 9:
            print('\ndone: ', i + 1)
        else:
            print(end=' %d ' % (i + 1))
            
    shell('git gc')  # run garbage colector

    print(f'Created {commit_count} commits in {repo_name}')


if __name__ == '__main__':
	make_repo_for_bisect('practice300', 300)
