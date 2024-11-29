import asyncio
from concerts_getter import ConcertsGetter
from app.models.common import Artist


# тесты make_url

def main():
    a = Artist()
    a.name = "MAYOT"
    b = Artist()
    b.name = "GONE.Fludd"
    c = Artist()
    c.name = "шаман"
    d = Artist()
    d.name = "Friendly Thug 52 NGG"
    e = Artist()
    e.name = "Люся Чеботина"

    obj = ConcertsGetter([a, b, c, d, e])
    ans = asyncio.run(obj.extract_concerts())
    for key in ans.keys():
        print(f"{key}: {ans[key]}")


if __name__ == "__main__":
    main()
