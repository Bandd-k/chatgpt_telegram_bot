import openai_utils
import unittest

#python -m unittest bot/test.py

async def check(student_last, bot_last, message) -> str:
    chatgpt_instance = openai_utils.ChatGPT()
    message_to_check_correction = f"""
    Student: {student_last}
    Teacher: {bot_last}
    Student: {message}
    """

    correction_answer, _, _ = await chatgpt_instance.send_message(
        message_to_check_correction,
        dialog_messages=[],
        chat_mode="correction_check"
    )
    return correction_answer


class TestCorrections(unittest.IsolatedAsyncioTestCase):
    async def test_easy(self):
        answer = await check("", "What did you eat today", "I eat a burger")
        self.assertNotEqual(answer, "✅ Correct!")

    async def test_easy2(self):
        answer = await check("", "What did you eat today", "I ate burger")
        self.assertNotEqual(answer, "✅ Correct!")

    async def test_easy3(self):
        answer = await check("", "What did you eat today", "I ate a burgers")
        self.assertNotEqual(answer, "✅ Correct!")

    async def test_easy4(self):
        answer = await check("", "What did you eat today", "I ate burgers. Burgers is my favorite foods")
        self.assertNotEqual(answer, "✅ Correct!")

    async def test_hard(self):
        message = """This morning, I treated myself to a delightful breakfast that kept me satisfied for hours.
        I began with a warm bowl of steel-cut oats, sweetened with a drizzle of honey and topped with a handful of vibrant, antioxidant-rich blueberries.
        To add some creaminess, I added a spoonful of thick Greek yogurt on top.
        Alongside my oatmeal, I enjoyed the tangy zest of a cold glass of orange juice, which I had freshly squeezed.
        I also prepared some fluffy scrambled eggs, lightly seasoned to perfection, and garnished them with fresh chives from my garden.
        To round off the meal, I had a slice of toasted whole-grain bread with a smooth, ripe avocado spread across it.
        It was a simple yet profoundly satisfying breakfast, and it gave me the perfect energy boost to start my day on a positive note."""
        answer = await check("", "What did you eat today", message)
        self.assertEqual(answer, "✅ Correct!")
        
    async def test_hard2(self):
        message = """This morning, I treated myself to a delightful breakfast that kept me satisfied for hours.
        I began with a warm bowl of steel-cut oats, sweetened with a drizzle of honey and topped with a handful of vibrant, antioxidant-rich blueberries.
        To add some creaminess, I added a spoonful of thick Greek yogurt on top.
        Alongside my oatmeal, I enjoyed the tangy zest of a cold glass of orange juice, which I had freshly squeezed.
        I also prepared some fluffy scrambled eggs, lightly seasoned to perfection, and garnished them with fresh chives from my garden.
        To round off the meal, I had a slice of toasted whole-grain bread with a smooth, ripe avocado spread across it.
        It were a simple yet profoundly satisfying breakfast, and it gave me the perfect energy boost to start my day on a positive note."""
        answer = await check("", "What did you eat today", message)
        print(answer)
        self.assertNotEqual(answer, "✅ Correct!")
        

if __name__ == '__main__':
    unittest.main()
