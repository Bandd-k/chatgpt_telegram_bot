import openai_utils
import unittest

#python3.9 -m unittest test.py 

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
    # async def test_easy(self):
    #     answer = await check("", "What did you eat today", "I eat a burger")
    #     self.assertNotEqual(answer, "✅ Correct!")

    # async def test_easy2(self):
    #     answer = await check("", "What did you eat today", "I ate burger")
    #     self.assertNotEqual(answer, "✅ Correct!")

    # async def test_easy3(self):
    #     answer = await check("", "What did you eat today", "I ate a burgers")
    #     self.assertNotEqual(answer, "✅ Correct!")

    # async def test_easy4(self):
    #     answer = await check("", "What did you eat today", "I ate burgers. Burgers is my favorite foods")
    #     self.assertNotEqual(answer, "✅ Correct!")

    # async def test_hard(self):
    #     message = """This morning, I treated myself to a delightful breakfast that kept me satisfied for hours.
    #     I began with a warm bowl of steel-cut oats, sweetened with a drizzle of honey and topped with a handful of vibrant, antioxidant-rich blueberries.
    #     To add some creaminess, I added a spoonful of thick Greek yogurt on top.
    #     Alongside my oatmeal, I enjoyed the tangy zest of a cold glass of orange juice, which I had freshly squeezed.
    #     I also prepared some fluffy scrambled eggs, lightly seasoned to perfection, and garnished them with fresh chives from my garden.
    #     To round off the meal, I had a slice of toasted whole-grain bread with a smooth, ripe avocado spread across it.
    #     It was a simple yet profoundly satisfying breakfast, and it gave me the perfect energy boost to start my day on a positive note."""
    #     answer = await check("", "What did you eat today", message)
    #     self.assertEqual(answer, "✅ Correct!")
        
    # async def test_hard2(self):
    #     message = """This morning, I treated myself to a delightful breakfast that kept me satisfied for hours.
    #     I began with a warm bowl of steel-cut oats, sweetened with a drizzle of honey and topped with a handful of vibrant, antioxidant-rich blueberries.
    #     To add some creaminess, I added a spoonful of thick Greek yogurt on top.
    #     Alongside my oatmeal, I enjoyed the tangy zest of a cold glass of orange juice, which I had freshly squeezed.
    #     I also prepared some fluffy scrambled eggs, lightly seasoned to perfection, and garnished them with fresh chives from my garden.
    #     To round off the meal, I had a slice of toasted whole-grain bread with a smooth, ripe avocado spread across it.
    #     It were a simple yet profoundly satisfying breakfast, and it gave me the perfect energy boost to start my day on a positive note."""
    #     answer = await check("", "What did you eat today", message)
    #     print(answer)
    #     self.assertNotEqual(answer, "✅ Correct!")

    # async def test_summarizer(self):
    #     chatgpt_instance = openai_utils.ChatGPT()
    #     conversation = [
    #         {"bot": "Good morning, Alex! Are you ready for today's English practice with me, Chatty?", "user": "Good morning, Chatty! Yes, I'm ready and looking forward to improving my speaking skills."},
    #         {"bot": "Fantastic, Alex! Let's start by discussing your recent trip. Tell me, what was the highlight of your visit to Brighton?", "user": "I think the highlight was seeing the sunset from Brighton Beach. It was breathtaking."},
    #         {"bot": "That sounds beautiful. Now, try to describe that sunset to me using some vivid adjectives.", "user": "The sky was ablaze with shades of orange and pink, and the sea reflected the colors like a giant mirror."},
    #         {"bot": "Well done, Alex! Your description really paints a picture. Moving on, have you read any interesting books lately?", "user": "Yes, I just finished reading '1984' by George Orwell. It was quite thought-provoking."},
    #         {"bot": "A classic choice! What did you find most intriguing about '1984'?", "user": "The concept of Big Brother and the idea of constant surveillance was really disturbing but intriguing."},
    #         {"bot": "It is a powerful theme. Could you tell me how it made you feel in one complete sentence?", "user": "It made me feel grateful for the freedoms we have, and it also made me more aware of privacy issues."},
    #         {"bot": "Excellent response, Alex. Now, shall we practice some future tense by talking about your plans for the holidays?", "user": "Sure, Chatty. I'm planning to go skiing in the Alps with my family. It's going to be an adventure."},
    #         {"bot": "That sounds exciting! How do you think you'll prepare for the trip?", "user": "I will take some skiing lessons and make sure I have all the necessary gear."},
    #         {"bot": "Good thinking. Now, let's switch to some conditional sentences. What would you do if you had a week off with no obligations?", "user": "If I had a week off, I would probably travel to Japan. I've always wanted to see the cherry blossoms."},
    #         {"bot": "Japan would be a great destination. What would be the first thing you'd do there?", "user": "I would visit the historic temples in Kyoto and try authentic Japanese sushi."},
    #         {"bot": "That sounds like a well-thought-out plan. Now, imagine you're at a job interview. How would you introduce yourself?", "user": "I would say, 'Hello, my name is Alex, and I am passionate about graphic design and creating innovative visual content.'"},
    #         {"bot": "Impressive introduction, Alex. Let's continue with the interview scenario. Why should we hire you for this position?", "user": "You should hire me because I have a unique creative vision, a strong work ethic, and a commitment to excellence in design."},
    #         {"bot": "You've made a compelling case, Alex. Now let's unwind with a simpler task. Tell me about your favorite season and why.", "user": "My favorite season is autumn. I love the cool weather, the colorful leaves, and the cozy atmosphere it brings."},
    #         {"bot": "Autumn is indeed a lovely season. Could you use autumn in a metaphorical sentence?", "user": "Sure, Chatty. 'The park, adorned in autumn's fiery hues, was a canvas painted with nature's final flourish before winter.'"},
    #     ]

    #     last_message = "Make summary of this conversation"
    #     summary_answer, _, _ = await chatgpt_instance.send_message(
    #     last_message,
    #     dialog_messages=conversation,
    #     chat_mode="summarizer"
    #     )
    #     print(summary_answer)

    async def test_summarizer2(self):
        chatgpt_instance = openai_utils.ChatGPT()
        conversation = [
        {
            'user': 'Hey I am Denis! I am 29. I am here to practice english',
            'bot': 'Nice to meet you Denis, If you could invite any three famous people to your party, who would they be and why?'
        },
        {
            'user': 'It\'s a tough question, I guess I would definitely invite Elon Musk and other two, for example Nikita Bayer, he is fun and he created a couple of cool apps and to make a party more elegant I would invite some beautiful girl, for example like Madison Beer.',
            'bot': 'Wow, that\'s quite a diverse guest list! Elon Musk, Nikita Bayer, and Madison Beer. It sounds like you\'re planning a party that\'s a mix of intellectual stimulation, entrepreneurial spirit, and a dash of glamour. I can imagine the conversations would be fascinating. Elon Musk could share his latest ideas about space travel, Nikita Bayer could talk about his new apps, and Madison Beer could lighten the mood with her charm and maybe even a song or two. \n\nBut let\'s make this scenario even more interesting. Imagine you have the chance to ask each of them one question that they have to answer honestly. What would you ask them?'
        },
        {
            'user': 'Questions for Nikita and Alan are pretty obvious. I would ask them to review my current projects, give me some tips, advice, and direction, and so on. And Madison Beer, I would ask her, do I have chance with her?',
            'bot': 'Haha, I see you\'re a man with a plan! Getting professional advice from Elon Musk and Nikita Bayer could be a game-changer for your projects. And as for Madison Beer, well, fortune favors the bold, right? \n\nBut let\'s imagine Madison says yes. What would be your ideal first date with her?',
        },
        {
            'user': 'Ideal for me is just to walk in a beautiful place where you have nice surroundings and we can speak to each other about my thoughts, her thoughts. I would ask her a lot of questions and maybe she would ask me back. So like good conversation in the middle of walking in the beautiful city center for example. And at the end of our walk we would have a dinner in a good place, have food and that\'s it. That\'s a perfect date like from my perspective.',
            'bot': 'That sounds like a perfect date indeed! A leisurely walk in a beautiful city center, engaging in deep conversation, and ending the day with a nice dinner. It\'s simple, yet intimate and meaningful. It\'s clear that you value genuine connection and getting to know someone on a deeper level. \n\nNow, let\'s switch gears a bit. If you could live in any city in the world, where would you choose and why?',
        },
        {
            'user': 'I used to live in Moscow, and I enjoyed it very much. Its one of the best places where you can live, I guess. Its pretty modern, and at the same time, Moscow has a lot of historical places, and everything is very clean. It\'s not dangerous here, and so on. A lot of opportunities, since it\'s one of the biggest capitals in the world. So maybe I would choose to go back there and live. Also, I would like to live in New York. I\'ve been in New York, and I feel it\'s a good place for me as well. I guess the cities are pretty similar in terms of opportunities. The both cities are very, very big, and a lot of money there. And about New York, I know there is a lot of places where I can work. I know a couple of guys there, my friends from university, so yeah, it would be good to live there. That\'s it.',
            'bot': 'It sounds like you have a deep appreciation for bustling, vibrant cities like Moscow and New York. both cities indeed offer a wealth of opportunities and have a unique blend of history and modernity. It\'s great that you have friends in New York too, that always makes a move easier. \n\nNow, let\'s imagine you\'re living in New York. You wake up one Saturday morning with no plans. What would your ideal day look like?',
        },
        {
            'user': 'As I said earlier, I like walking, so I would definitely visit Central Park in the morning. I would spend half an hour there just to start a good day. Then I would go back home or probably in a good co-working space with a beautiful city view. I would work on my project, very hard working, about five or six hours here. Then I would stop working and have some fun, for example, meet up with friends, maybe play some quiz game, something like that, eat delicious food, for example, burgers and coke with my friends, watch some movie, for example. So just relaxing and then go to sleep. That\'s my perfect day in New York City.',
            'bot': 'That sounds like a well-balanced day - a bit of nature, some productive work, and then unwinding with friends. Central Park is indeed a great place to start the day, and working with a city view sounds inspiring. And who can resist a good burger and a movie to end the day?\n\nSpeaking of movies, what\'s the last movie you watched that you really enjoyed and why did you like it?',
        },
        {
            'user': 'The last movie I watched, and I really enjoyed it, it\'s definitely Oppenheimer by Christopher Nolan. It\'s an amazing movie from every perspective. It\'s a perfect actor cast, it\'s perfect shooting, and in the middle of this film, it\'s a very interesting topic for me, it\'s physics, with Cold War like surrounding, it\'s Soviet Union versus USA, it\'s like Cold War battle run, so everything is just perfect for me. If I would need to tell you what aspects should be in perfect film for me, it would be all these aspects.',
            'bot': 'Ah, Christopher Nolan! He\'s a master at creating complex, thought-provoking films, and "Oppenheimer" is no exception. It\'s clear that you appreciate a well-crafted movie with a compelling storyline and strong performances. The historical context of the Cold War and the scientific aspect of physics add another layer of intrigue. \n\nNow, let\'s imagine you\'re given the opportunity to direct a movie. What would it be about and who would you cast in the lead roles?',
        },
        {
            'user': 'As I said earlier, for me, the best films are Interstellar or Oppenheimer, so I would be very proud to create such films. And also I really like Guy Ritchie films, so I would like to create something in style of Guy Ritchie as well. For example, Singed, Rock\'n\'Roller, it\'s a good movie as well, and I guess Actor\'s Cast and so on are perfect in this style as well.',
            'bot': 'Ah, a blend of Christopher Nolan\'s thought-provoking narratives and Guy Ritchie\'s unique style - that sounds like a recipe for a fantastic movie! It\'s clear that you have a deep appreciation for cinema and storytelling. \n\nNow, let\'s imagine you\'re on the set of this movie. What\'s the first scene you\'d shoot and why?',
        },
        {
            'user': 'I would shoot communication between main characters in unofficial surroundings, you know, and just to disclose some personal characteristics of these characters, yeah? And to make watchers see a little bit inside of these characters from the beginning of the story.',
            'bot': 'That\'s a great choice! Starting with a scene that reveals the personal characteristics of the main characters would definitely draw the audience in and make them invested in the story from the get-go. It\'s clear that you have a knack for storytelling. \n\nNow, let\'s switch gears a bit. If you could have any superpower, what would it be and why?',
        },
        {
            'user': 'For me, there are three top superpowers. It\'s first one, teleport. Second one, invisibility. And third one is immortality. It\'s hard to name the best one. So it depends on the situation. I would say that invisibility is the worst one out of these three. And immortality and teleport is like the best two options. With teleport, you can travel around the world and save a lot of time. You can be everywhere. You can enjoy sunset on one part of the world and then in another second, you already see sunrise and so on. Immortality gives you this opportunity to learn limitless amount of information. You can learn a lot of skills, languages, and so on. Yeah, you can spend a lot of time doing the stuff which is not very useful. Like, you can watch old TV movies or old TV shows and still have time to work, yeah. And you know, you can like, you have limitless amount of tries to do something and it gives you big chance to become successful, to make something meaningful in the world. And yeah, so that\'s it.',
            'bot': 'Wow, those are some well-thought-out choices! Teleportation would indeed be a fantastic way to see the world, and immortality would give you the chance to learn and experience so much. It\'s clear that you value knowledge, exploration, and making a meaningful impact. \n\nNow, let\'s imagine you have the power of teleportation for a day. Where\'s the first place you\'d teleport to and why?',
        },
        {
            'user': 'let\'s put aside all teleportations which allows me to earn somehow money you know like teleport once in place and get some money and something like that and so just use teleportation for travel purposes to see something yeah and I would teleport to the ocean beach in Australia yeah because it\'s very far for me to fly there and teleport would be an easy choice yeah to see to lay on the beach relax then I would go to another place maybe I would find some restricted closed beach yeah where you can can to go on your own yeah and teleport there also I can find some island where no boats coming and so on so the only way to come by teleport yeah it would be really really cool',
            'bot': 'That sounds like an amazing day! Teleporting to a secluded beach in Australia, then finding your own private island - it\'s like the ultimate vacation. And the best part is, no long flights or crowded tourist spots. Just you, the sun, and the ocean. \n\nNow, let\'s imagine you\'re on that private island. What\'s the one thing you\'d bring with you and why?',
        },
        {
            'user': 'If I can take a person, I would take my wife, so she would see this amazing view as well. I\'m sure she would be very happy, she would smile, and it boosts my positive mood as well.',
            'bot': 'That\'s so sweet! Sharing such a unique and beautiful experience with your wife would indeed make it even more special. It\'s clear that you deeply care about her happiness. \n\nNow, let\'s switch gears a bit. If you could have dinner with any historical figure, who would it be and why?',
        },
        {
            'user': 'hey',
            'bot': 'Hello again! So, as we were discussing, if you could have dinner with any historical figure, who would it be and why?',
        },
        {
            'user': 'It would be steve jobs',
            'bot': 'Ah, Steve Jobs, a visionary who truly changed the world. His innovative thinking and relentless drive are truly inspiring. What would be the first question you\'d ask him over dinner?',
        },
        {
            'user': 'I would ask him what idea should I work on',
            'bot': 'That\'s a very strategic question! Asking Steve Jobs for guidance on which idea to pursue could potentially set you on a path to great success. He had a knack for seeing the potential in ideas and bringing them to life in ways that resonated with people.\n\nNow, let\'s imagine Steve Jobs gave you a brilliant idea. What field or industry do you hope this idea would be in?',
        },
        {
            'user': '',
            'bot': 'Hello there! I noticed we haven\'t chatted in a while. I hope everything is going well with you. I was really enjoying our conversation about potential ideas and industries you might be interested in. If you have some time, I\'d love to hear more about your interests or any other topics you\'d like to discuss. Remember, practicing your English conversation skills can be about any subject that excites you. So, what\'s been on your mind lately?',
        },
        {
            'user': 'Tomorrow I\'m going to visit my friend in Moscow. I will have a flight in seven hours. We will spend a week together. Yeah, my friend and couple of other friends. Yeah, so we are going to have like cool holidays.',
            'bot': 'That sounds like an exciting trip! A week with friends in Moscow promises to be a memorable time. With the city\'s rich history and vibrant culture, there\'s so much to see and do. Plus, catching up with friends is always a great way to spend a holiday. \n\nSince you have a flight in seven hours, have you finished packing, or are you a last-minute packer?',
        },
        {
            'user': 'I am actually a last-minute packer, but yeah, but I will pack very soon. It won\'t be last minute this time, but it\'s not an early packing as well.',
            'bot': 'Living on the edge with last-minute packing—I like your style! It adds a little bit of thrill to the pre-trip routine, doesn\'t it? Just make sure you don\'t forget the essentials, like your passport, charger, and maybe a good book for the flight.\n\nSince you\'re going to be in Moscow, is there a particular place or activity you\'re most looking forward to during your visit?',
        },
        {
            'user': '',
            'bot': 'Hello! I hope your trip to Moscow went smoothly and that you\'re having a fantastic time with your friends. When you have a moment, I\'d love to hear about your adventures! Whether it\'s the places you\'ve visited, the food you\'ve tried, or any interesting conversations you\'ve had, feel free to share your experiences. Remember, talking about your travels can be a great way to practice your English. Looking forward to catching up with you soon. Enjoy your holiday!',
        },
        {
            'user': 'Thanks!',
            'bot': 'You\'re welcome! I hope you create lots of wonderful memories in Moscow. If you ever want to share stories from your trip or just chat about anything else, I\'m here. Have an amazing week with your friends and safe travels! What\'s the first thing you\'re planning to do when you arrive?',
        },
        {
            'user': '',
            'bot': 'Hello! Just checking in to see how your trip to Moscow is going. If you\'ve already started exploring, I\'d love to hear about your first impressions or any interesting experiences you\'ve had. Remember, sharing your travel stories is not only enjoyable but also a great way to practice your English. Whenever you\'re ready to chat, I\'m here. Hope you\'re having a great time!',
        },
        {
            'user': 'I spent quality time in Moscow!',
            'bot': 'That\'s fantastic to hear! Moscow is such a vibrant city with so much to offer. I bet you have some great stories to tell. What was one of the highlights from your trip that you\'ll always remember?',
        },
        {
            'user': 'Honestly, I think I will remember every day of this trip, but let\'s choose one. I would say it\'s birthday of my friend. We went to steakhouse and ordered the most delicious steakhouses in Moscow from Goodman restaurant.',
            'bot': 'Celebrating a friend\'s birthday at a steakhouse sounds like a wonderful highlight! Goodman restaurant is known for its quality, so it must have been quite the treat. Sharing good food in great company is always memorable. \n\nNow that you\'ve had such a rich experience, what\'s something new you\'d like to try or learn? It could be a new hobby, skill, or even a new cuisine to cook. What\'s piquing your interest these days?',
        },
        {
            'user': 'I would like to develop my painting skill. Sometimes I try to paint something in pop art style, like Alec Manopoli, but my skill is very low. I mean, I can imagine something cool. I have nice ideas. Yeah, in my opinion, obviously. But sometimes it\'s hard for me to put them on a board, you know.',
            'bot': 'That\'s a wonderful creative pursuit! Painting, especially in a style like pop art, can be incredibly rewarding. It\'s great that you have the ideas and the vision – that\'s a huge part of the creative process. Remember, every artist starts somewhere, and the more you paint, the more your skills will develop. \n\nHave you considered taking a class or following online tutorials to help refine your techniques? Sometimes a little guidance can go a long way in translating those cool ideas onto the canvas. What\'s the last piece you worked on, or what\'s an idea you\'re excited to bring to life?',
        },
        {
            'user': 'Now I want to create Mona Lisa pop art collage',
            'bot': 'That sounds like an ambitious and exciting project! Mona Lisa is such an iconic subject, and giving it a pop art twist would definitely create a unique piece. Pop art is all about bold colors and fun, so it\'s a great way to express your creativity. \n\nAs you embark on this artistic endeavor, remember to enjoy the process and not worry too much about the end result. Art is about expression and exploration. What elements or colors are you thinking of incorporating into your Mona Lisa pop art collage?',
        },
        {
            'user': 'I know it would be pink background, other colors are not decided yet',
            'bot': 'A pink background is a bold choice that can really make your Mona Lisa pop art collage stand out! Pink can offer a playful, modern vibe that contrasts nicely with the traditional image of the Mona Lisa. As for the other colors, you might consider classic pop art choices like bright yellows, reds, and blues to complement the pink and bring that vibrant pop art feel to life.\n\nRemember, there\'s no right or wrong in art—it\'s all about what feels right to you and what you want to convey. Have fun experimenting with different shades and see how they change the mood of the piece. What part of the process are you most excited about?',
        },
        {
            'user': 'The most exciting part is to put it on the wall.',
            'bot': 'Absolutely, there\'s something incredibly satisfying about hanging your own artwork on the wall. It\'s a moment of pride and accomplishment, seeing your vision realized and adding a personal touch to your space. Plus, it can be a great conversation starter when you have guests over!\n\nBefore you get to that thrilling moment, you\'ll have the creative journey of bringing your idea to life. Enjoy each brushstroke, and don\'t forget to step back occasionally to see the whole picture as it comes together. What room do you think you\'ll hang your Mona Lisa pop art collage in?',
        },
        {
            'user': 'I would hang it near the entrance in my flat, i mean inside',
            'bot': 'That\'s a prime spot! Hanging your Mona Lisa pop art collage near the entrance will ensure that it\'s one of the first things you and your guests see when entering your flat. It\'ll set a creative and welcoming tone right from the start. Plus, it\'s a great way to share your artistic side with anyone who visits.\n\nCreating a piece for such a prominent place can be really motivating, too. It\'s like you\'re creating your own personal gallery. I can\'t wait to hear about the reactions you\'ll get when it\'s up! What\'s inspiring you to choose Mona Lisa for this piece?',
        }
    ]

        last_message = "Make short summary about the student to use for future conversations"
        summary_answer, _, _ = await chatgpt_instance.send_message(
        last_message,
        dialog_messages=conversation,
        chat_mode="summarizer"
        )
        print(summary_answer)

#     async def test_summarizer_with_summary(self):
#         chatgpt_instance = openai_utils.ChatGPT()

#         prevsummary = ''' Information about the student
# - Denis, 29, practicing English.
# - Enjoys walking and deep conversations.
# - Interested in physics, Cold War history, and films like "Oppenheimer."
# - Appreciates cities like Moscow and New York for their opportunities and vibrancy.
# - Prefers last-minute packing for travel.
# - Recently visited Moscow, enjoyed a friend's birthday at Goodman steakhouse.
# - Wants to develop painting skills, particularly in pop art style.
# - Planning to create a Mona Lisa pop art collage with a pink background.
# - Intends to hang the finished artwork near the entrance of his flat.
# '''

#         conversation = [
#         {
#             'user': 'Probably collage would be pretty flat and contains not so many color, so I want it to be recognizible by everyone just by shape. And it mona lisa is a good candidate',
#             'bot': 'That\'s a smart approach! Using a universally recognized figure like the Mona Lisa ensures that your artwork will be immediately identifiable, allowing the pop art style and your unique interpretation to take center stage. By keeping the color palette limited, you can really play with the shapes and the composition to make a striking impact.\n\nIt\'s clever to rely on the power of silhouette and form, which can be just as expressive as a wide array of colors. I\'m sure your rendition will spark interest and admiration from those who see it. Are you planning to use any other iconic pop culture elements, or will Mona Lisa be the sole focus of your collage?',
#         },
#         {
#             'user': 'It will be the sole focus',
#             'bot': 'Focusing solely on the Mona Lisa will give you the opportunity to really delve deep into reimagining this iconic piece with a pop art twist. It\'s exciting to think about how you\'ll interpret her enigmatic expression and timeless features in a fresh, modern way.\n\nRemember, the beauty of pop art is in its bold simplicity and the way it can make a powerful statement with just a few elements. I can\'t wait to hear about the progress of your project and the final result. How do you plan to start your creative process for this collage?',
#         },
#         {
#             'user': 'I want to make a sketch using photoshop first, then order material for collage, it would be retro magazines',
#             'bot': 'Using Photoshop to sketch out your ideas is a fantastic way to experiment with different layouts and color schemes before committing to the actual collage. It gives you the flexibility to try out various concepts quickly and see what resonates with you the most. Plus, incorporating retro magazines will add an authentic pop art feel and a touch of nostalgia to your piece.\n\nSourcing the right magazines can be an adventure in itself, and you might find some unexpected inspiration in their pages. Are you looking for magazines from a specific era or just any that catch your eye with interesting imagery and text?',
#         },
#         {
#             'user': 'The second one, I’ll just take whatever catches my eye 🙂',
#             'bot': 'That\'s the spirit! Sometimes the best artistic choices come from spontaneous finds and serendipitous moments. As you sift through different magazines, you\'ll likely come across a wealth of visual treasures that can add depth, texture, and context to your collage. It\'s like a treasure hunt where each page can offer a new surprise that could take your artwork in an exciting direction.\n\nRemember to enjoy the process and let your intuition guide you. The pieces that catch your eye will come together to create something uniquely yours. What\'s the first step you\'re going to take to get this project underway?',
#         },
#         {
#             'user': 'As I said earlier, my first step is to make photoshop sketch, in particular to draw Mona Lisa the way I’ll create it using magazines pieces later',
#             'bot': 'Right, starting with the Photoshop sketch is a wise move. It\'ll serve as a blueprint for your collage, allowing you to visualize the end result and plan out the composition. Drawing Mona Lisa in this initial stage will help you figure out which parts of the magazines you\'ll need and how to piece them together.\n\nIt\'s like putting together a puzzle, except you get to decide the shape of the pieces. I\'m sure the process of translating your digital sketch into a physical collage will be both challenging and rewarding. How detailed do you plan to make your Photoshop sketch before you start working with the actual magazine pieces?',
#         },
#         {
#             'user': 'It would be pretty detailed, just to be sure I won’t fail anything during the real work',
#             'bot': 'That\'s a solid plan. A detailed Photoshop sketch will act as a comprehensive guide and can really help to minimize any uncertainties during the actual assembly of your collage. It\'s like having a map in a treasure hunt; it won\'t show you where all the little surprises are, but it\'ll definitely help you get to the X that marks the spot.\n\nTaking the time to refine your digital sketch can also give you a clearer sense of the scale and proportion of the different elements you\'ll be working with. Plus, it\'s a great way to experiment with different ideas without the pressure of making permanent changes. What aspect of creating this detailed sketch do you think will be the most challenging?',
#         },
#         {
#             'user': 'Create mona lisa the way I’ll be able to reproduce it using magazines pieces',
#             'bot': 'That does sound like a complex task, but also an intriguing one! Reproducing the Mona Lisa in a way that can be translated into magazine pieces will require a keen eye for detail and a good sense of abstraction. You\'ll need to break down the famous portrait into shapes and colors that can be represented by the clippings you\'ll find.\n\nThink of it as creating a mosaic; each piece of magazine clipping will be a tile that contributes to the overall image. It\'s about finding the right balance between detail and simplicity, ensuring that the essence of the Mona Lisa is captured even when the medium changes.\n\nAs you work on your sketch, consider the tones and textures in the magazines you have in mind. How do you envision balancing the iconic features of the Mona Lisa with the more abstract elements of pop art in your collage?',
#         }
#         ]

#         last_message = "Make short notes about the student to continue conversation later"
#         summary_answer, _, _ = await chatgpt_instance.send_message(
#         last_message,
#         dialog_messages=conversation,
#         chat_mode="summarizer",
#         additional_system=prevsummary
#         )
#         print(summary_answer)



    # async def test_conversationContinue(self):
    #     chatgpt_instance = openai_utils.ChatGPT()
    #     summary = '''
    #         Student: Alex
    #         Topics Discussed:
    #         1. English speaking practice
    #         2. Trip to Brighton - Highlight: Sunset at Brighton Beach
    #         3. Reading - '1984' by George Orwell, themes of surveillance and privacy
    #         4. Future plans - Skiing trip to the Alps, preparation and activities
    #         5. Hypothetical scenarios - Traveling to Japan, activities and experiences
    #         6. Job interview skills - Self-introduction, reasons for hiring
    #         7. Favorite season - Autumn, reasons and descriptive language

    #         Note: Alex is working on improving speaking skills, has a keen interest in literature, travel, and professional development, and is articulate in expressing thoughts and experiences.'''

    #     conversation = [
    #         {"bot": "You've made a compelling case, Alex. Now let's unwind with a simpler task. Tell me about your favorite season and why.", "user": "My favorite season is autumn. I love the cool weather, the colorful leaves, and the cozy atmosphere it brings."},
    #         {"bot": "Autumn is indeed a lovely season. Could you use autumn in a metaphorical sentence?", "user": "Sure, Chatty!"},
    #     ]
    #     last_message = "'The park, adorned in autumn's fiery hues, was a canvas painted with nature's final flourish before winter.'!"
    #     conversation_answer, _, _ = await chatgpt_instance.send_message(
    #     last_message,
    #     dialog_messages=conversation,
    #     chat_mode="general_english",
    #     additional_system=summary
    #     )
    #     print(conversation_answer)



if __name__ == '__main__':
    unittest.main()