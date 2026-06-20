def check_fn(k, v):
    print(k)
    print(v)


dictt = {
    'test1' : 'this is test1',
    'test2' : 'this is test2',
    'test3' : 'this is test3'
}

# print(len(dictt))

for key,value in dictt.items():
    check_fn(key,value)