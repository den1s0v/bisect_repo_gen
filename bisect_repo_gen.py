"""Генератор линейных git-репозиториев для практики git bisect."""

import argparse
import random
import shutil
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Создать git-репозиторий с N коммитами для практики bisect.',
    )
    parser.add_argument(
        'repo_name',
        nargs='?',
        default='practice100',
        help='имя папки репозитория внутри --output-dir (по умолчанию: practice100)',
    )
    parser.add_argument(
        '-n', '--commit-count',
        type=int,
        default=100,
        metavar='N',
        help='число коммитов и диапазон чисел 1..N (по умолчанию: 100)',
    )
    parser.add_argument(
        '-f', '--target-file',
        default='file.txt',
        help='имя файла в репозитории (по умолчанию: file.txt)',
    )
    parser.add_argument(
        '--broken-chance',
        type=float,
        default=0.1,
        metavar='P',
        help='вероятность «сломанного» коммита, 0..1 (по умолчанию: 0.1)',
    )
    parser.add_argument(
        '-o', '--output-dir',
        type=Path,
        default=Path('repos'),
        help='каталог для репозиториев (по умолчанию: repos)',
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        help='seed для random (воспроизводимая генерация)',
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='перезаписать существующий каталог репозитория',
    )
    args = parser.parse_args(argv)
    if args.commit_count < 1:
        parser.error('--commit-count must be at least 1')
    if not 0 <= args.broken_chance <= 1:
        parser.error('--broken-chance must be between 0 and 1')
    return args


def run_git(args: list[str], cwd: Path) -> None:
    """Выполнить git-команду в каталоге cwd."""
    result = subprocess.run(
        ['git', *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        cmd = ' '.join(['git', *args])
        stderr = result.stderr.strip()
        raise RuntimeError(f'git failed ({result.returncode}): {cmd}\n{stderr}')


class CommitContentProvider:
    """Формирует содержимое file.txt для каждого коммита."""

    def __init__(self, top: int, broken_chance: float) -> None:
        self.pool = set(range(1, top + 1))
        self.content: list[str] = []
        self.commit_n = 0
        self.broken_chance = broken_chance

    def prepare_content(self) -> list[str]:
        next_from_pool = random.choice(list(self.pool))
        self.pool.remove(next_from_pool)

        value = f'{next_from_pool:03d}'
        insert_pos = random.randint(0, len(self.content))
        self.content.insert(insert_pos, value)

        self.commit_n += 1
        return self.content

    def get_content_for_commit(self) -> str:
        lines = self.prepare_content()
        if len(self.pool) > 1 and random.random() < self.broken_chance:
            sep = ''
            header = (
                f'Это сломанный коммит № {self.commit_n}, '
                'в котором что-то сделано, но нельзя понять, что именно.'
            )
        else:
            sep = '\n'
            header = (
                f'Это нормальный коммит № {self.commit_n}, '
                'в котором можно найти искомое число.'
            )

        return f'{header}\n\n{sep.join(lines)}\n'

    def generate_commits(self) -> Iterator[str]:
        while self.pool:
            yield self.get_content_for_commit()


def make_repo_for_bisect(
    repo_path: Path,
    commit_count: int = 100,
    target_file_name: str = 'file.txt',
    broken_chance: float = 0.1,
    force: bool = False,
) -> None:
    """Создать git-репозиторий с commit_count коммитами в repo_path."""
    if repo_path.exists():
        if not force:
            raise FileExistsError(
                f'Каталог уже существует: {repo_path}. '
                'Используйте --force для перезаписи.',
            )
        shutil.rmtree(repo_path)

    repo_path.mkdir(parents=True)
    run_git(['init'], repo_path)

    ccp = CommitContentProvider(commit_count, broken_chance)

    for i, content in enumerate(ccp.generate_commits()):
        target = repo_path / target_file_name
        target.write_text(content, encoding='utf-8')

        run_git(['add', target_file_name], repo_path)
        run_git(['commit', '-m', f'commit-{i + 1}'], repo_path)

        if i % 10 == 9:
            print(f'\ndone: {i + 1}')
        else:
            print(f' {i + 1} ', end='')

    run_git(['gc'], repo_path)
    print(f'\nCreated {commit_count} commits in {repo_path}')


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if args.seed is not None:
        random.seed(args.seed)

    repo_path = args.output_dir / args.repo_name
    try:
        make_repo_for_bisect(
            repo_path=repo_path,
            commit_count=args.commit_count,
            target_file_name=args.target_file,
            broken_chance=args.broken_chance,
            force=args.force,
        )
    except (FileExistsError, RuntimeError) as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
