# -*- coding: utf-8 -*-
import requests
import json
import datetime
import urllib.request


sCorpID = "ww9e41923879199f79"
corpsecret = "CApTe8BBqDy2sUQlzCjeadettAw-MspNB-PXeRCq_Fw"
agentID=1000004

API_PATHS = {
    "GET_TOKEN_URL" : "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s",
    "SEND_MESSAGE"  : "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s",
    #上传媒体接口，其中参数access_token 为生成的令牌,type 是指媒体类型 有图片（image）、语音（voice）、视频（video），普通文件(file)
    "UPLOAD_MEDIA"  : "https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=%s",
}

MSGTYPES = {
    'text':{
        'content':'',
    },
    'image':{
        'media_id':'',
    },
    'news':{
        'articles':[],
    }
}


class Article(object):
    """暂时不用"""
    def __init__(self,title,description='',url='',picurl=''):
        self.title = title
        self.description = description
        self.url = url
        self.picurl = picurl

class Message(object):
    """
    消息类型的基本类
    """    
    def __init__(self,agentid,touser='',toparty='',totag='',safe=0):
        """
        初始化方法
        Args:
            touser : 成员ID列表（消息接收者，多个接收者用‘|’分隔，最多支持1000个）。
                     特殊情况：指定为@all，则向关注该企业应用的全部成员发送.非必填.
            agentid: 企业应用的id，整型。可在应用的设置页面查看.
            toparty: 部门ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
            totag  : 标签ID列表，多个接收者用‘|’分隔。当touser为@all时忽略本参数
            safe   : 表示是否是保密消息，0表示否，1表示是，默认0
        """
        self.agentid = agentid
        self.touser = touser
        self.toparty = toparty
        self.totag = totag
        self.safe = safe

class TextMessage(Message):
    """
    文本类型消息
    """
    def __init__(self,agentid,touser='',toparty='',totag='',safe=0,content=''):
        """
        初始化方法
        Args:
            touser : 成员ID列表（消息接收者，多个接收者用‘|’分隔，最多支持1000个）。
                     特殊情况：指定为@all，则向关注该企业应用的全部成员发送.非必填.
            agentid: 企业应用的id，整型。可在应用的设置页面查看.
            toparty: 部门ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
            totag  : 标签ID列表，多个接收者用‘|’分隔。当touser为@all时忽略本参数
            safe   : 表示是否是保密消息，0表示否，1表示是，默认0.
            content: 消息内容
        """
        self.msgtype = "text"
        self.text = {"content": content }
        Message.__init__(self,agentid,touser,toparty,totag,safe)


class BinaryMessage(Message):
    """
    附件类消息的基类
    """
    def __init__(self,agentid,touser='',toparty='',totag='',safe=0,type=None,media_id=''):
        self.msgtype = type
        self.__setattr__(type,{'media_id': media_id})
        Message.__init__(self,agentid,touser,toparty,totag,safe)

class FileMessage(BinaryMessage):
    """
    普通文件消息
    """
    def __init__(self,agentid,touser='',toparty='',totag='',safe=0,media_id=''):
        BinaryMessage.__init__(self,agentid,touser,toparty,totag,safe,"file",media_id)

class ImageMessage(BinaryMessage):
    """
    图片类型消息
    """
    def __init__(self,agentid,touser='',toparty='',totag='',safe=0,media_id=''):
        BinaryMessage.__init__(self,agentid,touser,toparty,totag,safe,"image",media_id)


class VoiceMessage(BinaryMessage):
    """
    声音类型消息
    """
    def __init__(self,agentid,touser='',toparty='',totag='',safe=0,media_id=''):
        BinaryMessage.__init__(self,agentid,touser,toparty,totag,safe,"voice",media_id)


class VideoMessage(BinaryMessage):
    """
    视频类型消息
    """
    def __init__(self,agentid,touser='',toparty='',totag='',safe=0,media_id='',title='',description=''):
        BinaryMessage.__init__(self,agentid,touser,toparty,totag,safe,"voice",media_id)
        content_attr = self.__getattribute__("voice")
        content_attr["title"] = title
        content_attr["description"] = description
        

class NewsMessage(Message):
    """
    news消息
    """
    def __init__(self,agentid,touser='',toparty='',totag='',safe=0,news=[]):
        """
        初始化方法
        Args:
            news : 消息列表，结构如下[Article(),Article(),...]
        """
        self.news = {"articles":news}
        self.msgtype = "news"
        Message.__init__(self,agentid,touser,toparty,totag,safe)


class MessageEncoder(json.JSONEncoder):
    """
    对Message提供Encode类
    """
    def default(self,obj):
        if isinstance(obj,Article):
            return obj.__dict__
        return obj


class WXBizSendMsg(object):
    
    def __init__(self,sCorpID,corpsecret):
        self.sCorpID = sCorpID
        self.corpsecret = corpsecret
        self.access_token = None
        self.access_token_generate_time = None
    '''
    def verify(self,stoken,msg_signature,timestamp,echostr,nonce):
        """
        验证企业号的回调URL的有效性
        Args:
            stoken:       应用上设置的用于回调的token.
            msg_signature:微信加密签名，msg_signature结合了企业填写的token、请求中的timestamp、nonce参数、加密的消息体.
            timestamp:    时间戳.
            echostr:      加密的随机字符串，以msg_encrypt格式提供。需要解密并返回echostr明文，
                          解密后有random、msg_len、msg、$CorpID四个字段，其中msg即为echostr明文.
            nonce:        随机数.
        Returns:
            ret:          为0时表验证成功，其他返回值请参考微信官方文档.
            sEchoStr:     解密之后的echostr，当ret返回0时有效
        """
        echostr = urllib.unquote(echostr)
        wxcpt = WXBizMsgCrypt(stoken,self.corpsecret,sCorpID)
        ret,sEchoStr = wxcpt.VerifyURL(msg_signature[0],timestamp,nonce,echostr)
        return ret,sEchoStr
        '''

    def _get_valid_access_token(self):
        """
        如果token生成的时间范围是7200秒以内，则直接获取缓存值
        """
        if not self.access_token or not self.access_token_generate_time:
            return None
        end_time = datetime.datetime.now()
        if (end_time - self.access_token_generate_time).total_seconds()<7200:
            print('catch cache') 
            return self.access_token
        else:
            return None

    def get_access_token(self):
        """
        获取token,7200秒内有效,此处可以加缓存机制处理，这里只能在一个实例中有效
        """
        access_token = self._get_valid_access_token()
        if not access_token:
            res = requests.get(API_PATHS["GET_TOKEN_URL"]%(self.sCorpID,self.corpsecret))
            access_token = res.json()["access_token"]
            self.access_token = access_token
            self.access_token_generate_time = datetime.datetime.now()
        return access_token

    def upload_media(self,type,file_path):
        """
        上传媒体文件接口
        Args:
            type     : 文件类型,分别有图片（image）、语音（voice）、视频（video），普通文件(file).
            file_path: 文件在服务器上的地址.
        Returns:
            media_id: "0000001",
        """
        #TODO 文件类型检查
        #TODO 文件大小检查
        #图片（image）:1MB，支持JPG格式, 语音（voice）：2MB，播放长度不超过60s，支持AMR格式
        #视频（video）：10MB，支持MP4格式
        #普通文件（file）：10MB
        send_url = API_PATHS["UPLOAD_MEDIA"] % (self.get_access_token(),type)
        files = {"file":open(file_path,'rb')}
        res = requests.post(send_url,files=files)
        return res.json()["media_id"]

    def send_message(self,message):
        """
        发送消息给微信
        Args:
            token,验证用的token.
            message,需要发送的消息，为Message类的子类对象
        Returns:
            发送结果
        """
        send_url = API_PATHS["SEND_MESSAGE"] % self.get_access_token()
        #data = json.dumps(message.__dict__,cls=MessageEncoder,ensure_ascii=False)
        #用utf-8编码
        data =bytes(json.dumps(message.__dict__,cls=MessageEncoder,ensure_ascii=False), 'utf-8')
        res = requests.post(send_url,data=data)
        return res.json()


def test_send_txt():
    api = WXBizSendMsg(sCorpID,corpsecret)
    message = TextMessage(agentID,touser='@all',content='这是一条测试消息')
    res = api.send_message(message)
    print(res)

def test_send_pic():
    api = WXBizSendMsg(sCorpID,corpsecret)
    media_id = api.upload_media("file","D:/python_study/images/bg.jpg")
    message = ImageMessage(agentID,touser="@all",media_id=media_id)
    res = api.send_message(message)
    print(res)

def test_send_file():
    api = WXBizSendMsg(sCorpID,corpsecret)
    media_id = api.upload_media("file","D:/python_study/images/bg.jpg")
    message = FileMessage(agentID,touser="@all",media_id=media_id)
    res = api.send_message(message)
    print(res)

def test_send_news():
    news = [
        Article("新西兰众议院男议长一边给娃喂奶一边主持会议","","http://slide.news.sina.com.cn/w/slide_1_2841_390472.html","https://n.sinaimg.cn/news/175/w105h70/20190823/e8f0-icqznfz9777841.jpg"),
        Article("世锦赛男单1/8决赛：谌龙2-1苦战险胜伍家朗","","http://slide.sports.sina.com.cn/o/slide_2_730_225698.html","https://n.sinaimg.cn/sports/transform/175/w105h70/20190823/b8b5-icqznfz9276721.jpg"),
            ]
    message = NewsMessage(agentID,touser="@all",news=news)
    api = WXBizSendMsg(sCorpID,corpsecret)
    res = api.send_message(message)
    print(res)

if __name__ =="__main__":
    test_send_txt()
    test_send_pic()
    test_send_news()
    

