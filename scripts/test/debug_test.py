import pdb

def add(a,b):
    print a,b
    return a+b

def mul(a,b):
    print a,b
    return a*b

def main():
    a = 1
    b = 2

    c = add(a,b)

    d = mul(c,b)

    return a,b,c,d

if __name__ == "__main__":
    pdb.set_trace()
    print main()
