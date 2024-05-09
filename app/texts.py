from enum import Enum
from config.config_reader import config


class LangEnum(Enum):
    russian = 1
    english = 2


class CheckTypeEnum(Enum):
    file = 1
    link = 2


class CommandText:

    def get_start_text(lang: LangEnum):
        start_text = (
            "Привет! Я бот-антивирус @awesomeantivirus_bot. Отправь мне файл или ссылку и я проверю его по базе антивирусов virustotal.com",
            "Hi! I am @awesomeantivirus_bot, antivirusbot. Send my the file or link and I'll check it by antivirus base from virustotal.com",
        )

        if lang == LangEnum.russian:
            return start_text[0]
        else:
            return start_text[1]

    def get_about_text(lang: LangEnum):
        about_text = (
            "Привет! Я бот-антивирус @awesomeantivirus_bot. Отправь мне файл или ссылку и я проверю его по базе антивирусов virustotal.com",
            "Hi! I am @awesomeantivirus_bot, antivirusbot. Send my the file or link and I'll check it by antivirus base from virustotal.com",
        )

        if lang == LangEnum.russian:
            return about_text[0]
        else:
            return about_text[1]

    def get_stats_text(lang: LangEnum, files_number: int, links_number: int):
        if lang == LangEnum.russian:
            stats_text = f"Сегодня вы проверили {files_number} файла/ов и {links_number} ссыл(ок)/(у)"
        else:
            stats_text = (
                f"Today you checked {files_number} file/s и {links_number} link/s"
            )

        return stats_text


class FileDialogText:

    def get_big_file_text(lang: LangEnum, filename: str, filesize: str):
        big_file_text = (
            f"Файл {filename} слишком большой для проверки. \nЕго размер - <b>{filesize}</b>. \nМаксимальный размер файла <b>{config.max_size_mb} МБ</b>",
            f"File {filename} is too big for analysis. \nIt's size is <b>{filesize}</b>. \nMaximum file size is <b>{config.max_size_mb} МБ</b>",
        )

        if lang == LangEnum.russian:
            return big_file_text[0]
        else:
            return big_file_text[1]

    def get_cancel_check_text(lang: LangEnum, filename: str = None):
        cancel_check_text = (
            f"❌ Отменена проверка файла {filename if filename else ''}",
            f"❌ File check cancelled for {filename if filename else ''}",
        )
        if lang == LangEnum.russian:
            return cancel_check_text[0]
        else:
            return cancel_check_text[1]

    def get_all_checked(lang: LangEnum, datatype: CheckTypeEnum):
        all_files_checked_text = ("Все файлы проверены 😎", "All files checked 😎")

        all_links_checked_text = ("Все ссылки проверены 😎", "All links checked 😎")

        if lang == LangEnum.russian:
            if datatype == CheckTypeEnum.file:
                return all_files_checked_text[0]
            else:
                return all_links_checked_text[0]
        else:
            if datatype == CheckTypeEnum.file:
                return all_files_checked_text[1]
            else:
                return all_links_checked_text[1]

    def get_limit_req_text(lang: LangEnum, limit: int, datatype: CheckTypeEnum):

        data = ""
        if datatype == CheckTypeEnum.file:
            if lang == LangEnum.russian:
                data = "файлов"
            else:
                data = "files"

        if datatype == CheckTypeEnum.link:
            if lang == LangEnum.russian:
                data = "ссылок"
            else:
                data = "links"

        files_req_limit_text = (
            f"К сожалению вы достигли лимита в {limit} {data} в день.",
            f"Sorry, you have reached the daily limit of {limit} for {data} analysis requests.",
        )
        if lang == LangEnum.russian:
            return files_req_limit_text[0]
        else:
            return files_req_limit_text[1]

    def get_error_analizing_text(
        lang: LangEnum, filename: str, datatype: CheckTypeEnum
    ):

        data = ""
        if datatype == CheckTypeEnum.file:
            if lang == LangEnum.russian:
                data = "файла"
            else:
                data = "file"

        if datatype == CheckTypeEnum.link:
            if lang == LangEnum.russian:
                data = "ссылки"
            else:
                data = "link"

        error_alalizing_text = (
            f"Произошла ошибка при анализе {data} {filename}",
            f"Sorry, there was an error analyzing the {data} {filename}",
        )

        if lang == LangEnum.russian:
            return error_alalizing_text[0]
        else:
            return error_alalizing_text[1]

    @staticmethod
    def get_result_file_text(
        lang: LangEnum,
        dangerous_files: int,
        number_checks: int,
        filename: str,
        filesize: str,
        link: str,
    ):

        if lang == LangEnum.russian:
            result = f"""
{"‼️‼️‼️ Внимание! В файле обнаружены возможные угрозы!" if dangerous_files > 0 else ""}
📁 Имя файла : {filename}
💿 Размер файла : {filesize}


🦠 Обнаружено <a href = '{link}'>{dangerous_files} угроз</a> из {number_checks} проверок.
"""
        else:
            result = f"""
{"‼️‼️‼️ Attention! Potential threats in this file!" if dangerous_files > 0 else ""}
📁 Name of the file : {filename}
💿 File size : {filesize}

🦠 Found <a href = '{link}'>{dangerous_files} threats</a> doing {number_checks} checks.
"""
        return result

    @staticmethod
    def get_result_link_text(
        lang: LangEnum,
        dangerous_files: int,
        number_checks: int,
        orig_link: str,
        link: str,
        domain: str,
    ):
        if lang == LangEnum.russian:
            result = f"""
{"‼️‼️‼️ Внимание! В ссылке обнаружены возможные угрозы!" if dangerous_files > 0 else ""}       
📁 Ссылка : {orig_link}
🌐 Домен : {domain}

🦠 Обнаружено <a href = '{link}'>{dangerous_files} угроз</a> из {number_checks} проверок. 

{f"Сервис не гарантирует правдивости предоставленной на сайте {domain} информации, а только проверет сайт на наличие вирусов." if not dangerous_files > 0 else ""}
"""
        else:
            result = f"""
{"‼️‼️‼️ Attention! Potential threats in this link!!" if dangerous_files > 0 else ""}       
📁 Link : {link}
🌐 Domain : {domain}

🦠 Found <a href = '{link}'>{dangerous_files} threats</a> doing {number_checks} checks. 

{f"Service doesnt guarantee the legitimacy of the information on {domain} - only check the link for viruses." if not dangerous_files > 0 else ""}
"""
        return result
