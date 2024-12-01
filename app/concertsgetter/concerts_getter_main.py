import asyncio

from app.concertsgetter.concerts_getter import ConcertsGetter
from app.models.common import Artist


def main():
    names = ["MAYOT", "GONE.Fludd", "Шаман", "Люся Чеботина"]
    artists = [Artist(names[i], (i + 1) / 10) for i in range(len(names))]

    obj = ConcertsGetter(artists)
    ans = asyncio.run(obj.extract_concerts())
    print(f"len(ans) = {len(ans)}")
    print(f"ans: {ans}")


if __name__ == "__main__":
    main()
