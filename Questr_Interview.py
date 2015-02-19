__author__ = 'Michael'

''' print fibonacci numbers '''


def memoize(f):
    d = {}

    def func(arg):
        if arg in d.keys():
            return d[arg]
        ans = f(arg)
        d[arg] = ans
        return ans

    return func


@memoize # this is the syntax to do the two commented lines on the bottom.
def fib(n):
    if n == 0:
        print(0)
        return 0
    elif n == 1:
        ans = fib(0) + 1
        print(ans)
        return ans
    else:
        ans = fib(n - 2) + fib(n - 1)
        print(ans)
        return ans


# fib = memoize(fib)
# fib(10)

fib(10)
