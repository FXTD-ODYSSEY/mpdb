# from __future__ import print_function
import mpdb

def add(a,b):
    print (a,b)
    return a+b

def mul(a,b):
    print (a,b)
    return a*b

def main():
    a = 1
    b = 2

    mpdb.set_trace()
    c = add(a,b)

    # mpdb.set_trace()
    d = mul(c,b)

    print (a,b,c,d)
    return a,b,c,d

if __name__ == "__main__":
    mpdb.set_trace()
    main()

    print "done"


