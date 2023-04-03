# Генератор линейных git-репозиториев для практики bisect

## Требования:
- Python 3

## Идея:
- Сыграйте с Git в игру "угадай число", т.е. "найди коммит, в котором число было добавлено" (числа не повторяются).
- Диапазон чисел: от 1 до N, где N - размер генерируемого репозитория.
- В каждом коммите добавляется одно число из диапазона, выбраное случайным образом, и вставленное в случайное место файла.
- Для интереса, некоторые коммиты специально "испорчены", имитируя несобираемые коммиты (тем не менее, при желании, найти в нём добавленное число можно ;-) ).


## Генерация репозитория:
- в файле `bisect_repo_gen.py` изменить имя репозитория и число коммитов в нём, как требуется:
`make_repo_for_bisect('practice300', 300)`
- запустить `python bisect_repo_gen.py` (или `python3 bisect_repo_gen.py`)

- Если не хватает "испорченных" коммитов, можно увеличить значение константы `CHANCE_OF_BROKEN_COMMIT` (в диапазоне от 0 до 1).
