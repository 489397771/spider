from PIL import Image
def get_captcha(url):
    """
    url: 传入验证码图片的url
    """
    r = requests.get(url)
    with open('captcha.jpg', 'wb') as f:
        f.write(r.content)
        f.close()
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
    captcha = input("please input the captcha\n>")
    return captcha
