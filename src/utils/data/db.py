import abc

class DBMeta(abc.ABCMeta):
    def __new__(mcls, classname, bases, cls_dict):
        cls = super().__new__(mcls, classname, bases, cls_dict)
        for name, member in cls_dict.items():
            if not getattr(member, '__doc__'):
                member.__doc__ = getattr(bases[-1], name).__doc__ if hasattr(bases[-1], name) else None
        return cls

class DBInterface(object, metaclass=DBMeta):

    @abc.abstractmethod
    def ask_collection(self, id):
        """
        Check for existence of Collections

        :param id: An ID or list of IDs
        :return: A value between 0 and 1 - 0=none, 0.x=some, 1=all
        """
        pass

    @abc.abstractmethod
    def get_collection(self, id=None):
        """
        Retrieve Collection data

        :param id: An ID, a list of IDs or nothing (returns all)
        :return: A list of Collection objects
        """
        pass

    @abc.abstractmethod
    def set_collection(self, c_obj):
        """
        Store Collection data

        :param c_obj: A Collection object or a list of Collection objects
        :return:
        """
        pass

    @abc.abstractmethod
    def del_collection(self, id):
        """
        Delete Collection data

        :param id: A collection ID
        :return:
        """
        pass

    @abc.abstractmethod
    def upd_collection(self, c_obj):
        """
        Update Collection data

        :param c_obj: A Collection object with an existing ID
        :return:
        """
        pass



    @abc.abstractmethod
    def ask_member(self, cid, mid):
        """
        Check for existence of MemberItems

        :param cid: A collection id
        :param mid: An ID or list of IDs
        :return: A value between 0 and 1 - 0=none, 0.x=some, 1=all
        """
        pass

    @abc.abstractmethod
    def get_member(self, cid, mid=None):
        """
        Retrieve Member data

        :param cid: A Collection ID
        :param mid: An ID, a list of IDs or nothing
        :return: A list of MemberItem objects
        """
        pass

    @abc.abstractmethod
    def set_member(self, c_id, m_obj):
        """
        Store MemberItem data

        :param c_id: A Collection ID
        :param m_obj: A MemberItem object or list of MemberItem objects
        :return:
        """
        pass

    @abc.abstractmethod
    def del_member(self, c_id, m_id):
        """
        Delete MemberItem data

        :param c_id: A Collection ID
        :param m_id: An ID or list of IDs
        :return:
        """
        pass

    @abc.abstractmethod
    def upd_member(self, c_id, m_obj):
        """
        Update MemberItem data

        :param c_id: A Collection ID
        :param m_obj: A MemberItem object with an existing ID
        :return:
        """
        pass



    @abc.abstractmethod
    def get_service(self):
        """

        :return:
        """
        pass

    @abc.abstractmethod
    def set_service(self, s_obj):
        """

        :param s_obj:
        :return:
        """
        pass



    @abc.abstractmethod
    def get_id(self, type):
        """

        :param type:
        :return:
        """
        pass
