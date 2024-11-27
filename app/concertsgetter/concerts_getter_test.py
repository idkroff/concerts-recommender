import asyncio
from concerts_getter import ConcertsGetter
from app.models.common import Artist


def main():
    a = Artist()
    a.name = "MAYOT"
    b = Artist()
    b.name = "GONE.Fludd"
    c = Artist()
    c.name = "шаман"
    d = Artist()
    d.name = "Friendly Thug 52 NGG"

    obj = ConcertsGetter([a, b, c, d])
    ans = asyncio.run(obj.extract_concerts())
    for el in ans:
        print(el)


if __name__ == "__main__":
    main()
