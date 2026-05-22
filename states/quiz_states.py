from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    waiting_for_book_title = State()
    waiting_for_pdf        = State()


class BookStates(StatesGroup):
    waiting_for_page_range = State()


class QuizStates(StatesGroup):
    answering = State()
