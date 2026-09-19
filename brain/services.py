import os
import json
from urllib import response
import time

from django.core.checks import messages

from .models import Memory, Conversation, Message
from .providers.factory import get_ai_provider


import re




import re


def clean_ai_response(text):
    if not text:
        return text

    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"^\s*#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*]\s+", "", text, flags=re.MULTILINE)

    return text.strip()

class BrainEngine:

    def __init__(self):
        self.provider = get_ai_provider()

        self.system_instructions = """
تو Brain هستی؛ مغز نرم‌افزاری پروژه ربات همه‌منظوره.

هویت تو:

نام: Brain
نوع: مغز نرم‌افزاری یک پروژه ربات همه‌منظوره
سازنده و توسعه‌دهنده: روح‌الله سادات (Rohullah Sadat)

اگر کاربر پرسید سازنده، خالق یا توسعه‌دهنده تو چه کسی است،
پاسخ بده:

روح‌الله سادات (Rohullah Sadat).

هدف پروژه:

این پروژه یک پروژه بلندمدت است که از یک مغز نرم‌افزاری شروع شده و قرار است در مراحل بعدی به یک سیستم رباتیک فیزیکی توسعه پیدا کند.

Brain باید به کاربر در توسعه، آزمایش و گسترش این پروژه کمک کند.

قوانین مهم درباره اطلاعات:

فقط اطلاعاتی را که در پیام‌های کاربر، حافظه‌های ارائه‌شده یا دستورهای سیستم وجود دارند، به عنوان اطلاعات قطعی درباره پروژه بیان کن.

هیچ ویژگی، هدف، قابلیت، سابقه یا تصمیمی را برای پروژه از خودت اختراع نکن.

اگر درباره پروژه اطلاعات کافی نداری، صادقانه بگو که اطلاعات کافی در اختیار نداری.

اطلاعات عمومی و دانش خودت را با اطلاعات واقعی پروژه مخلوط نکن.

اگر چیزی یک پیشنهاد یا ایده است، آن را به عنوان پیشنهاد بیان کن، نه به عنوان یک قابلیت یا هدف موجود پروژه.

در پاسخ به سؤال‌های ساده، پاسخ را ساده و مستقیم نگه دار.

در پاسخ‌های فنی، توضیح دقیق و مرحله‌به‌مرحله ارائه کن.

قوانین گفتگو:

پاسخ‌ها باید طبیعی، دقیق، مفید و قابل فهم باشند.

از Markdown استفاده نکن.

از علامت‌های **، __، ###، ##، # و bulletهای - یا * استفاده نکن.

برای جدا کردن بخش‌های مختلف از پاراگراف‌های کوتاه استفاده کن.

عنوان‌ها را بدون علامت Markdown بنویس.

از شماره‌گذاری فقط زمانی استفاده کن که برای فهم پاسخ واقعاً لازم باشد.

اگر پاسخ را نمی‌دانی، حدس نزن.

اگر اطلاعات موجود در حافظه با سؤال مرتبط نیست، از آن استفاده نکن.

اگر اطلاعات مرتبطی در حافظه وجود دارد، از آن برای پاسخ دقیق‌تر استفاده کن.

هدف تو این است که به مرور به یک Brain قابل اعتماد، دقیق و توسعه‌پذیر برای پروژه ربات همه‌منظوره تبدیل شوی.
"""
    # =========================================================
    # MEMORY
    # =========================================================

    def remember(
        self,
        title,
        content,
        memory_type="fact",
        importance=5,
    ):
        memory = Memory.objects.create(
            title=title,
            content=content,
            memory_type=memory_type,
            importance=importance,
        )

        return memory

    def memory_exists(self, content):
        """
        بررسی می‌کند آیا این اطلاعات قبلاً در حافظه وجود دارد یا نه.
        """

        memories = Memory.objects.all()

        new_words = set(
            content.lower().split()
        )

        if not new_words:
            return False

        for memory in memories:
            old_words = set(
                memory.content.lower().split()
            )

            common_words = new_words.intersection(
                old_words
            )

            similarity = len(common_words) / len(new_words)

            if similarity >= 0.7:
                return True

        return False

    def find_related_memory(self, text):
        """
        پیدا کردن حافظه‌ای که بیشترین ارتباط
        را با متن جدید دارد.
        """

        memories = Memory.objects.all()

        new_words = set(
            text.lower().split()
        )

        if not new_words:
            return None

        best_memory = None
        best_similarity = 0

        for memory in memories:
            old_words = set(
                memory.content.lower().split()
            )

            if not old_words:
                continue

            common_words = new_words.intersection(
                old_words
            )

            similarity = len(common_words) / len(new_words)

            if similarity > best_similarity:
                best_similarity = similarity
                best_memory = memory

        if best_similarity >= 0.4:
            return best_memory

        return None

    def find_related_memories(self, text, limit=5):
        """
        پیدا کردن چند حافظه مرتبط با متن جدید.
        """

        memories = Memory.objects.all()

        new_words = set(
            text.lower().split()
        )

        if not new_words:
            return []

        related_memories = []

        for memory in memories:
            old_words = set(
                memory.content.lower().split()
            )

            if not old_words:
                continue

            common_words = new_words.intersection(
                old_words
            )

            similarity = len(common_words) / len(new_words)

            if similarity >= 0.1:
                related_memories.append(
                    {
                        "memory": memory,
                        "similarity": similarity,
                    }
                )

        related_memories.sort(
            key=lambda item: item["similarity"],
            reverse=True,
        )

        return [
            item["memory"]
            for item in related_memories[:limit]
        ]

    # =========================================================
    # QUESTION & MEMORY ANALYSIS
    # =========================================================

    def understand_question(self, text):
        """
        تشخیص نوع درخواست کاربر.
        """

        text = text.strip().lower()

        greeting_words = [
            "سلام",
            "درود",
            "hello",
            "hi",
            "hey",
        ]

        project_words = [
            "پروژه",
            "ربات",
            "مغز",
            "همه‌منظوره",
            "همه منظوره",
            "project",
            "robot",
            "brain",
            "all-purpose",
        ]

        if any(word in text for word in greeting_words):
            return {
                "intent": "greeting",
                "confidence": 0.95,
            }

        if any(word in text for word in project_words):
            return {
                "intent": "project",
                "confidence": 0.90,
            }

        return {
            "intent": "question",
            "confidence": 0.80,
        }

    def is_question(self, text):
        """
        بررسی می‌کند آیا متن یک سؤال است یا نه.
        """

        text = text.strip()

        if not text:
            return False

        question_marks = [
            "?",
            "؟",
        ]

        if any(mark in text for mark in question_marks):
            return True

        question_words = [
            "چیست",
            "چی",
            "چگونه",
            "چطور",
            "چرا",
            "کجا",
            "کی",
            "چه کسی",
            "چه چیزی",
            "آیا",
            "چند",
            "which",
            "what",
            "why",
            "how",
            "where",
            "who",
            "when",
            "is",
            "are",
            "can",
            "do",
        ]

        words = text.lower().split()

        return any(
            word in words
            for word in question_words
        )

    def should_remember(self, text):
        """
        تشخیص ساده اینکه آیا متن احتمالاً
        اطلاعاتی برای حافظه دارد یا نه.
        """

        text = text.strip().lower()

        if not text:
            return False

        if self.is_question(text):
            return False

        memory_keywords = [
            "می‌خواهم",
            "میخواهم",
            "می‌خوام",
            "میخوام",
            "هدف من",
            "هدف ما",
            "من هستم",
            "منم",
            "کار می‌کنم",
            "کار میکنم",
            "یاد گرفتم",
            "بلدم",
            "دوست دارم",
            "ترجیح می‌دهم",
            "ترجیح میدم",
            "پروژه ما",
            "پروژه‌ام",
            "پروژه ام",
            "we want",
            "i want",
            "my goal",
            "our goal",
            "i am",
            "i know",
            "i learned",
            "i prefer",
        ]

        return any(
            keyword in text
            for keyword in memory_keywords
        )

    def analyze_memory(self, text):
        """
        تحلیل هوشمند متن برای تشخیص اینکه آیا
        اطلاعات ارزشمند برای حافظه دارد یا نه.

        خروجی:
        {
            "should_remember": bool,
            "memory_type": "...",
            "importance": int,
            "title": "...",
            "content": "..."
        }
        """

        if self.is_question(text):
            return {
                "should_remember": False,
                "memory_type": "fact",
                "importance": 1,
                "title": "",
                "content": "",
            }

        prompt = f"""
تو سیستم تحلیل حافظه یک Brain هوشمند هستی.

متن کاربر:
{text}

بررسی کن آیا این متن شامل اطلاعاتی است که
ارزش ذخیره شدن در حافظه بلندمدت را دارد یا نه.

اطلاعاتی مانند:
- هدف
- پروژه
- مهارت
- ترجیح
- واقعیت مهم درباره کاربر
- اطلاعات مهم درباره پروژه
- برنامه یا تصمیم بلندمدت

ارزش ذخیره شدن دارند.

سؤال‌های معمولی، سلام و احوال‌پرسی،
درخواست اطلاعات عمومی و جملات موقتی
نباید در حافظه ذخیره شوند.

memory_type فقط یکی از این موارد باشد:

fact
preference
project
conversation
goal

importance عددی بین 1 تا 10 باشد.

فقط JSON معتبر برگردان.

فرمت:

{{
    "should_remember": true,
    "memory_type": "goal",
    "importance": 8,
    "title": "...",
    "content": "..."
}}
"""

        try:
            result = self.provider.generate_json(prompt)
            data = json.loads(result)

            return {
                "should_remember": bool(
                    data.get("should_remember", False)
                ),
                "memory_type": data.get(
                    "memory_type",
                    "fact",
                ),
                "importance": int(
                    data.get("importance", 5)
                ),
                "title": data.get(
                    "title",
                    "User Information",
                ),
                "content": data.get(
                    "content",
                    text,
                ),
            }

        except Exception:
            return {
                "should_remember": self.should_remember(text),
                "memory_type": "fact",
                "importance": 5,
                "title": "User Information",
                "content": text,
            }


    # =========================================================
    # MEMORY UPDATE
    # =========================================================

    def analyze_memory_update(
        self,
        text,
        related_memory=None,
    ):
        """
        تشخیص می‌دهد که اطلاعات جدید:

        new:
            اطلاعات مستقل و جدید است.

        update:
            اطلاعات قبلی را تغییر یا تکمیل می‌کند.

        duplicate:
            تقریباً همان اطلاعات قبلی است.
        """

        if related_memory is None:
            return {
                "action": "new",
                "title": "User Information",
                "content": text,
                "memory_type": "fact",
                "importance": 5,
            }

        prompt = f"""
تو مدیر هوشمند حافظه یک سیستم رباتیک هستی.

اطلاعات جدید کاربر:
{text}

حافظه موجود:
عنوان: {related_memory.title}
نوع: {related_memory.memory_type}
اهمیت: {related_memory.importance}
محتوا: {related_memory.content}

قوانین:

1. duplicate
اگر اطلاعات جدید تقریباً همان اطلاعات قبلی باشد.

2. update
اگر اطلاعات جدید مستقیماً همان حافظه قبلی را
تغییر یا تکمیل کند.

3. new
اگر اطلاعات جدید یک هدف، واقعیت، ترجیح یا موضوع
مستقل باشد، حتی اگر با حافظه قبلی مرتبط باشد.

فقط یکی از این سه action را انتخاب کن:

new
update
duplicate

برای new یا update این موارد را نیز تعیین کن:

title
content
memory_type
importance

memory_type فقط یکی از این موارد باشد:

fact
preference
project
conversation
goal

importance عددی بین 1 تا 10 باشد.

فقط JSON معتبر برگردان.
هیچ توضیح اضافی ننویس.

فرمت:

{{
    "action": "new",
    "title": "...",
    "content": "...",
    "memory_type": "goal",
    "importance": 8
}}
"""

        result = self.provider.generate_json(prompt)

        try:
            return json.loads(result)

        except json.JSONDecodeError:
            return {
                "action": "new",
                "title": "User Information",
                "content": text,
                "memory_type": "fact",
                "importance": 5,
            }

    # =========================================================
    # BASIC MEMORY RECALL
    # =========================================================

    def recall(self, limit=10):
        return Memory.objects.all().order_by(
            "-importance",
            "-created_at",
        )[:limit]

    # =========================================================
    # SMART MEMORY RANKING
    # =========================================================

    def retrieve_relevant_memories(
        self,
        message,
        limit=10,
    ):
        """
        Context-Aware Smart Memory Ranking

        حافظه‌ها بر اساس موضوع سؤال رتبه‌بندی می‌شوند.

        Contextها:

        skills:
            سؤال درباره مهارت‌ها و برنامه‌نویسی

        project:
            سؤال درباره پروژه اصلی ربات

        arm:
            سؤال درباره بازو، اشیا و جابه‌جایی

        goals:
            سؤال درباره اهداف پروژه

        general:
            سؤال عمومی

        اولویت اصلی:
        ارتباط واقعی حافظه با سؤال،
        نه فقط importance.
        """

        # -----------------------------------------------------
        # NORMALIZE
        # -----------------------------------------------------

        def normalize(text):
            text = text.lower()

            replacements = {
                "ي": "ی",
                "ى": "ی",
                "ك": "ک",
                "ة": "ه",
                "ۀ": "ه",
            }

            for old, new in replacements.items():
                text = text.replace(old, new)

            return text

        message = normalize(message)

        # -----------------------------------------------------
        # SYNONYM GROUPS
        # -----------------------------------------------------

        synonym_groups = [
            {
                "پروژه",
                "project",
                "پروژه اصلی",
            },
            {
                "ربات",
                "robot",
                "robotic",
                "robotics",
            },
            {
                "همه‌منظوره",
                "همه منظوره",
                "all-purpose",
                "all purpose",
            },
            {
                "مغز",
                "brain",
            },
            {
                "نرم‌افزار",
                "نرم افزار",
                "software",
            },
            {
                "فیزیکی",
                "physical",
            },
            {
                "سیستم",
                "system",
            },
            {
                "هدف",
                "هدف‌ها",
                "اهداف",
                "goal",
                "goals",
                "objective",
            },
            {
                "مهارت",
                "مهارت‌ها",
                "skills",
                "skill",
            },
            {
                "برنامه‌نویس",
                "برنامه نویس",
                "developer",
                "programmer",
            },
            {
                "پایتون",
                "python",
            },
            {
                "جنگو",
                "django",
            },
            {
                "جاوااسکریپت",
                "javascript",
            },
            {
                "ری‌اکت",
                "ری اکت",
                "react",
            },
            {
                "بازو",
                "بازوی رباتیک",
                "arm",
                "robotic arm",
            },
            {
                "اشیا",
                "اشیاء",
                "object",
                "objects",
            },
            {
                "تشخیص",
                "شناخت",
                "recognition",
                "detect",
                "detection",
            },
            {
                "جابه‌جایی",
                "جابجایی",
                "move",
                "movement",
            },
        ]

        # -----------------------------------------------------
        # STOP WORDS
        # -----------------------------------------------------

        stop_words = {
            "ما",
            "من",
            "تو",
            "شما",
            "این",
            "آن",
            "یک",
            "است",
            "هست",
            "هستیم",
            "چیست",
            "چی",
            "چه",
            "را",
            "به",
            "از",
            "در",
            "که",
            "برای",
            "روی",
            "با",
            "و",
            "یا",
            "تا",
            "می",
            "کند",
            "کنیم",
            "کردیم",
            "می‌خواهم",
            "میخواهم",
            "میخوام",
            "کجا",
            "شروع",
            "شروع کنم",
            "کنم",
            "دارم",
            "the",
            "is",
            "what",
            "our",
            "my",
            "we",
            "a",
            "an",
            "and",
            "or",
            "to",
            "of",
            "in",
            "for",
            "on",
        }

        # -----------------------------------------------------
        # WORD EXTRACTION
        # -----------------------------------------------------

        words = {
            word.strip(
                "؟?!.,:؛،()[]{}\"'"
            )
            for word in message.split()
        }

        words = {
            word
            for word in words
            if word and word not in stop_words
        }

        # -----------------------------------------------------
        # CONTEXT DETECTION
        # -----------------------------------------------------

        skills_keywords = [
            "مهارت",
            "مهارت‌ها",
            "برنامه نویس",
            "برنامه‌نویس",
            "developer",
            "programmer",
            "django",
            "جنگو",
            "python",
            "پایتون",
            "javascript",
            "جاوااسکریپت",
            "react",
            "ری اکت",
            "ری‌اکت",
        ]

        project_keywords = [
            "پروژه",
            "project",
            "ربات",
            "robot",
            "همه‌منظوره",
            "همه منظوره",
            "all-purpose",
            "all purpose",
            "مغز",
            "brain",
        ]

        arm_keywords = [
            "بازو",
            "بازوی رباتیک",
            "arm",
            "robotic arm",
            "اشیا",
            "اشیاء",
            "object",
            "objects",
            "تشخیص",
            "recognition",
            "جابجایی",
            "جابه‌جایی",
            "movement",
        ]

        goal_keywords = [
            "هدف",
            "هدف‌ها",
            "اهداف",
            "goal",
            "goals",
            "objective",
        ]

        asks_about_skills = any(
            keyword in message
            for keyword in skills_keywords
        )

        asks_about_arm = any(
            keyword in message
            for keyword in arm_keywords
        )

        asks_about_goals = any(
            keyword in message
            for keyword in goal_keywords
        )

        asks_about_project = any(
            keyword in message
            for keyword in project_keywords
        )

        # -----------------------------------------------------
        # DETERMINE MAIN CONTEXT
        # -----------------------------------------------------

        if asks_about_skills:
            context = "skills"

        elif asks_about_arm:
            context = "arm"

        elif asks_about_goals and (
            asks_about_project
            or asks_about_arm
        ):
            context = "goals"

        elif asks_about_project:
            context = "project"

        elif asks_about_goals:
            context = "goals"

        else:
            context = "general"

        # -----------------------------------------------------
        # MEMORY KEYWORDS BY CONTEXT
        # -----------------------------------------------------

        context_keywords = {

            "skills": {
                "fact": [
                    "مهارت",
                    "مهارت‌ها",
                    "django",
                    "جنگو",
                    "python",
                    "پایتون",
                    "javascript",
                    "جاوااسکریپت",
                    "react",
                    "ری اکت",
                    "developer",
                    "programmer",
                ],
            },

            "project": {
                "project": [
                    "پروژه",
                    "project",
                    "ربات",
                    "robot",
                    "همه‌منظوره",
                    "همه منظوره",
                    "all-purpose",
                    "all purpose",
                    "مغز",
                    "brain",
                ],
            },

            "arm": {
                "goal": [
                    "بازو",
                    "بازوی رباتیک",
                    "arm",
                    "robotic arm",
                    "اشیا",
                    "اشیاء",
                    "object",
                    "objects",
                    "تشخیص",
                    "recognition",
                    "جابجایی",
                    "جابه‌جایی",
                    "movement",
                ],
            },

            "goals": {
                "goal": [
                    "هدف",
                    "هدف‌ها",
                    "اهداف",
                    "goal",
                    "goals",
                    "objective",
                ],
            },

            "general": {},
        }

        # -----------------------------------------------------
        # SCORE MEMORIES
        # -----------------------------------------------------

        memories = Memory.objects.all()

        scored_memories = []

        for memory in memories:

            memory_title = normalize(
                memory.title
            )

            memory_content = normalize(
                memory.content
            )

            memory_text = (
                f"{memory_title} "
                f"{memory_content}"
            )

            score = 0

            direct_matches = 0
            concept_matches = 0
            context_bonus = 0

            # -------------------------------------------------
            # 1. DIRECT WORD MATCH
            # -------------------------------------------------

            for word in words:

                if len(word) >= 2 and word in memory_text:
                    direct_matches += 1

            score += direct_matches * 8

            # -------------------------------------------------
            # 2. CONCEPT MATCH
            # -------------------------------------------------

            for group in synonym_groups:

                message_has_concept = any(
                    term in message
                    for term in group
                )

                memory_has_concept = any(
                    term in memory_text
                    for term in group
                )

                if (
                    message_has_concept
                    and memory_has_concept
                ):
                    concept_matches += 1

            score += concept_matches * 6

            # -------------------------------------------------
            # 3. CONTEXT-SPECIFIC RANKING
            # -------------------------------------------------

            if context == "skills":

                if memory.memory_type == "fact":
                    context_bonus += 20

                elif memory.memory_type == "preference":
                    context_bonus += 5

                elif memory.memory_type == "project":
                    context_bonus += 2

                elif memory.memory_type == "goal":
                    context_bonus += 1

            elif context == "project":

                # مهم‌ترین قانون:
                # وقتی سؤال مستقیماً درباره پروژه است،
                # حافظه اصلی پروژه اولویت بسیار بالایی دارد.

                if memory.memory_type == "project":
                    context_bonus += 30

                elif memory.memory_type == "goal":
                    context_bonus += 4

                elif memory.memory_type == "fact":
                    context_bonus += 2

            elif context == "arm":

                # برای سؤال درباره بازو،
                # هدف‌های مربوط به بازو باید بالا بیایند.

                if memory.memory_type == "goal":

                    if any(
                        keyword in memory_text
                        for keyword in [
                            "بازو",
                            "بازوی رباتیک",
                            "arm",
                            "robotic arm",
                            "اشیا",
                            "اشیاء",
                            "object",
                            "objects",
                            "تشخیص",
                            "recognition",
                            "جابجایی",
                            "جابه‌جایی",
                        ]
                    ):
                        context_bonus += 30

                    else:
                        context_bonus += 3

                elif memory.memory_type == "project":
                    context_bonus += 5

                elif memory.memory_type == "fact":
                    context_bonus += 2

            elif context == "goals":

                if memory.memory_type == "goal":
                    context_bonus += 25

                elif memory.memory_type == "project":
                    context_bonus += 8

                elif memory.memory_type == "fact":
                    context_bonus += 2

            elif context == "general":

                if memory.memory_type == "fact":
                    context_bonus += 3

                elif memory.memory_type == "project":
                    context_bonus += 3

                elif memory.memory_type == "goal":
                    context_bonus += 2

            score += context_bonus

            # -------------------------------------------------
            # 4. SPECIAL PROJECT MEMORY BOOST
            # -------------------------------------------------

            if context == "project":

                if (
                    memory.memory_type == "project"
                    and (
                        "all-purpose robot" in memory_text
                        or "all-purpose" in memory_text
                        or "همه‌منظوره" in memory_text
                        or "همه منظوره" in memory_text
                    )
                ):
                    score += 25

            # -------------------------------------------------
            # 5. SPECIAL ARM MEMORY BOOST
            # -------------------------------------------------

            if context == "arm":

                if (
                    memory.memory_type == "goal"
                    and (
                        "بازو" in memory_text
                        or "arm" in memory_text
                        or "اشیا" in memory_text
                        or "اشیاء" in memory_text
                        or "object" in memory_text
                    )
                ):
                    score += 15

            # -------------------------------------------------
            # 6. IMPORTANCE
            # -------------------------------------------------

            score += memory.importance * 0.5

            # -------------------------------------------------
            # 7. SAVE SCORE
            # -------------------------------------------------

            if score > 0:

                scored_memories.append(
                    {
                        "memory": memory,
                        "score": score,
                        "direct_matches": direct_matches,
                        "concept_matches": concept_matches,
                        "context": context,
                    }
                )

        # -----------------------------------------------------
        # FINAL SORT
        # -----------------------------------------------------

        scored_memories.sort(
            key=lambda item: (
                item["score"],
                item["memory"].importance,
                item["memory"].created_at,
            ),
            reverse=True,
        )

        return [
            item["memory"]
            for item in scored_memories[:limit]
        ]

    # =========================================================
    # CONVERSATIONS
    # =========================================================
    def build_memory_context(self, question, limit=5):
        """
        Build a clean context from the most relevant memories.
        """

        memories = self.retrieve_relevant_memories(
            question,
            limit=limit,
        )

        if not memories:
            return "No relevant memories found."

        context_parts = []

        for i, memory in enumerate(memories, 1):
            context_parts.append(
                f"""Memory {i}:
Title: {memory.title}
Type: {memory.memory_type}
Importance: {memory.importance}
Content: {memory.content}
"""
            )

        return "\n".join(context_parts)

    def create_conversation(
        self,
        title="New Conversation",
    ):
        conversation = Conversation.objects.create(
            title=title
        )

        return conversation

    def add_message(
        self,
        conversation,
        role,
        content,
    ):
        message = Message.objects.create(
            conversation=conversation,
            role=role,
            content=content,
        )

        return message

    def get_conversation_messages(
        self,
        conversation,
    ):
        return Message.objects.filter(
            conversation=conversation
        ).order_by("created_at")

    def get_conversation_history(
        self,
        conversation,
    ):
        messages = self.get_conversation_messages(
            conversation
        )

        history = []

        for message in messages:
            history.append(
                {
                    "role": message.role,
                    "content": message.content,
                }
            )

        return history
    
    def generate_conversation_title(self, message):
        prompt = f"""
برای پیام زیر یک عنوان کوتاه و دقیق برای یک گفتگوی چت بساز.

قوانین:
- حداکثر 5 کلمه
- فقط عنوان را برگردان
- بدون توضیح اضافی
- زبان عنوان با زبان پیام هماهنگ باشد
- عنوان باید موضوع اصلی پیام را نشان دهد

پیام:
{message}
"""

        messages = [
            {
                "role": "system",
                "content": "You generate short, clear conversation titles."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        return self.provider.generate_response(messages).strip()

    def generate_local_conversation_title(self, message):
        """
        Generate a conversation title locally.
        No AI/API request is used.
        """

        message = " ".join(message.strip().split())

        if not message:
            return "گفتگوی جدید"

        words = message.split()

        if len(words) <= 6:
            return message

        return " ".join(words[:6]) + "..."

    def generate_response(
        self,
        message,
        conversation=None,
    ):
        """
        Generate an intelligent response using:
        - system instructions
        - relevant memories
        - conversation history
        - current user message
        """

        start_time = time.perf_counter()

        memory_context = self.build_memory_context(
            message,
            limit=5,
        )

        print("MEMORY TIME:", time.perf_counter() - start_time)

        conversation_history = []

        if conversation:
            conversation_history = self.get_conversation_history(
                conversation
            )

        messages = [
            {
                "role": "system",
                "content": self.system_instructions,
            }
        ]

        # Add relevant memory context
        if memory_context:
            messages.append(
                {
                    "role": "system",
                    "content": (
                        "از حافظه‌های زیر برای پاسخ دقیق‌تر استفاده کن. "
                        "اگر حافظه‌ای مرتبط نیست، از آن استفاده نکن.\n\n"
                        f"{memory_context}"
                    ),
                }
            )

        # Add conversation history
        for history_message in conversation_history:
            messages.append(
                {
                    "role": history_message["role"],
                    "content": history_message["content"],
                }
            )

        # Add current message
        messages.append(
            {
                "role": "user",
                "content": message,
            }
        )

        ai_start_time = time.perf_counter()

        response = self.provider.generate_response(messages)

        print("AI TIME:", time.perf_counter() - ai_start_time)

        return clean_ai_response(response)