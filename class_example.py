#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# @Description: 
# @PreInstall: 
# @Author : https://www.bajins.com
# @File : class_example.py
# @Version: 1.0.0
# @Time : 2021/9/7 15:07
# @Project: python_learning
# @Package: 
# @Software: PyCharm


# self和cls的区别不是强制的，只是PEP8中一种编程风格，slef通常用作实例方法的第一参数，cls通常用作类方法的第一参数
class A(object):
    def foo(self, x):
        print("executing foo(%s,%s)" % (self, x))
        print('self:', self)

    @classmethod
    def class_foo(cls, x):
        print("executing class_foo(%s,%s)" % (cls, x))
        print('cls:', cls)

    @staticmethod  # 与普通函数相同
    def static_foo(x):
        print("executing static_foo(%s)" % x)


if __name__ == '__main__':
    print(dir(A()))  # 查看所有属性和方法，包含继承的object类内建属性和方法
    g = globals()  # 查看所有全局变量
    print(g)
    print(g['__builtins__'].__dict__)
