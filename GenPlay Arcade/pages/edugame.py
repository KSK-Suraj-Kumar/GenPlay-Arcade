import streamlit as st
import pygame
import random
import sys
import time
import google.generativeai as genai
import os
import mysql.connector
from login import login

# Redirect to Login if not authenticated
if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("You must log in first!")
        time.sleep(3)
        st.switch_page("login.py")

st.set_page_config(page_title="Snake Word Game", layout="centered")

st.title("🐍 Snake Word Game 🪄")
st.markdown("""
Control the snake with arrow keys.  
Eat the letters of each word **in the correct order** to grow. (Hint: Go after the **Yellow** highlighted letter)  
Avoid the walls and don't eat the wrong letter!      
After clicking 'Start game', press any arrow key to start!!     
Good Luck and Happy learning!!!
""")

username = st.text_input("Username")

# ---------- BACKGROUND & STYLES ----------
st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(to right, #01b3ef, #2e5caf);
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: white;
        }
        .stButton>button {
            width: 100%;
            background-color: #4CAF50;
            color: white;
            border-radius: 10px;
            padding: 15px;
        }
        .stButton>button:hover {
            background-color: #ffffff;
            color: green;
            transform: scale(1.05);
            } </style>
    """, unsafe_allow_html=True)

#topic = st.text_input("Enter a topic (e.g., Nouns, Verbs, Adjectives):")

if st.button("Begin adventure"):
    
# Initialize Gemini API
    GENAI_API_KEY = "YOUR_GEMINI_API_KEY"  #  Replace 'YOUR_GEMINI_API_KEY' with your actual API key.
    genai.configure(api_key=GENAI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')

    def get_random_word():
        prompt ="give a single word between 4 and 10 letters long. Strictly don't give any word more than the limit."
        response = model.generate_content(prompt)
        word = response.text.strip().split("\n")[0]
        return word.upper()

    def get_word_details(word):
        prompt = f"Give me the part of speech and a simple meaning of the word '{word}' in this format:\nPart of Speech: ...\nMeaning: ..."
        response = model.generate_content(prompt)
        details = response.text.strip()
    
    # Basic parsing for part of speech and meaning
        part_of_speech = "Unknown"
        meaning = "No meaning found."

        for line in details.split('\n'):
            if line.lower().startswith("part of speech"):
                part_of_speech = line.split(":")[-1].strip()
            elif line.lower().startswith("meaning"):
                meaning = line.split(":")[-1].strip()

        return part_of_speech, meaning

# Game Constants
    WIDTH, HEIGHT = 600, 600
    BLOCK_SIZE = 30
    FPS = 6

# Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

# Initialize Pygame
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Word Game")

    def draw_grid():
        for x in range(0, WIDTH, BLOCK_SIZE):
            pygame.draw.line(win, (40, 40, 40), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, BLOCK_SIZE):
            pygame.draw.line(win, (40, 40, 40), (0, y), (WIDTH, y))

    def wait_for_key_press():
        """Wait until any arrow key is pressed."""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
                waiting = False

    def show_word_details(word):
        """Display word, part of speech, and meaning for 3 seconds."""
        part_of_speech, meaning = get_word_details(word)
        win.fill(BLACK)

        font = pygame.font.SysFont('Arial', 32)
        small_font = pygame.font.SysFont('Arial', 24)

        word_text = font.render(f"Word: {word}", True, WHITE)
        pos_text = small_font.render(f"Part of Speech: {part_of_speech}", True, YELLOW)
        meaning_text = small_font.render(f"Meaning: {meaning}", True, GREEN)

        win.blit(word_text, (WIDTH // 2 - word_text.get_width() // 2, HEIGHT // 2 - 60))
        win.blit(pos_text, (WIDTH // 2 - pos_text.get_width() // 2, HEIGHT // 2))
        win.blit(meaning_text, (WIDTH // 2 - meaning_text.get_width() // 2, HEIGHT // 2 + 40))

        pygame.display.update()
        time.sleep(3)  # Pause for 3 seconds

    def show_final_score(score):
        """Display final score screen."""
        win.fill(BLACK)
        font = pygame.font.SysFont('Arial', 48)
        small_font = pygame.font.SysFont('Arial', 32)

        game_over_text = font.render("Game Over!", True, RED)
        score_text = small_font.render(f"Your Score: {score}", True, WHITE)
        instruction_text = small_font.render("Press any key to exit.", True, YELLOW)

        win.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 60))
        win.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        win.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT // 2 + 60))

        pygame.display.update()

    # Wait for any key press to exit
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            if any(keys):
                waiting = False

    def main():
        clock = pygame.time.Clock()
        snake = [(WIDTH // 2, HEIGHT // 2)]
        direction = (0, 0)
        current_word = get_random_word()
        print(f"New Word: {current_word}")
        letters = []
        letter_index = 0
        score = 0  # Start the score at zero

        def spawn_letters(word):
            positions = []
            while len(positions) < len(word):
                pos = (random.randint(0, (WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE,
                   random.randint(0, (HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE)
                if pos not in snake and pos not in positions:
                    positions.append(pos)
            return dict(zip(positions, word))

        letters = spawn_letters(current_word)

        running = True
        game_paused = True  # Initially paused before movement starts

        while running:
            clock.tick(FPS)
            win.fill(BLACK)
            draw_grid()

        # Handle quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
        
        # Start movement after player presses a key
            if game_paused:
                wait_for_key_press()
                game_paused = False
                direction = (0, 0)  # Snake is still until the keypress

        # Key handling for movement
            if keys[pygame.K_LEFT] and direction != (BLOCK_SIZE, 0):
                direction = (-BLOCK_SIZE, 0)
            elif keys[pygame.K_RIGHT] and direction != (-BLOCK_SIZE, 0):
                direction = (BLOCK_SIZE, 0)
            elif keys[pygame.K_UP] and direction != (0, BLOCK_SIZE):
                direction = (0, -BLOCK_SIZE)
            elif keys[pygame.K_DOWN] and direction != (0, -BLOCK_SIZE):
                direction = (0, BLOCK_SIZE)

        # Move snake
            if direction != (0, 0):
                new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

            # Collision with wall
                if (new_head[0] < 0 or new_head[0] >= WIDTH or
                    new_head[1] < 0 or new_head[1] >= HEIGHT):
                    print("Hit the wall! Game over.")
                    running = False
                    continue

            # Collision with self
                if new_head in snake:
                    print("Hit yourself! Game over.")
                    running = False
                    continue

                snake.insert(0, new_head)

            # Eating letter
                if new_head in letters:
                    letter = letters[new_head]
                    expected_letter = current_word[letter_index]

                    if letter == expected_letter:
                        print(f"Ate correct letter: {letter}")
                        letter_index += 1
                        del letters[new_head]

                        if letter_index == len(current_word):
                            # Finished the word! Show word info and pause
                            show_word_details(current_word)

                            # Increase the score by 1 for each completed word
                            score += 1
                            print(f"Score: {score}")

                        # Generate new word
                            current_word = get_random_word()
                            print(f"New Word: {current_word}")
                            letter_index = 0
                            letters = spawn_letters(current_word)

                        # Reset snake direction to pause after new word
                            game_paused = True
                            direction = (0, 0)

                    else:
                        print(f"Ate wrong letter! Expected {expected_letter}, but got {letter}. Game over.")
                        running = False
                        continue
                else:
                    snake.pop()  # Move forward normally

        # Draw snake
            for segment in snake:
                pygame.draw.rect(win, GREEN, (segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE))

            # Draw letters
            font = pygame.font.SysFont('Arial', 24)
            for pos, letter in letters.items():
            # Highlight the next expected letter in YELLOW
                if letter == current_word[letter_index]:
                    text = font.render(letter, True, YELLOW)
                else:
                    text = font.render(letter, True, RED)

                win.blit(text, (pos[0] + 5, pos[1] + 2))

        # Display current word and progress
            info_font = pygame.font.SysFont('Arial', 20)
            word_progress = current_word[:letter_index] + '_' * (len(current_word) - letter_index)
            info_text = info_font.render(f"Current Word: {word_progress}", True, WHITE)
            score_text = info_font.render(f"Score: {score}", True, WHITE)

            win.blit(info_text, (10, 10))
            win.blit(score_text, (10, 40))

            pygame.display.update()

    # After game loop ends, show the final score
        show_final_score(score)
        save_score(username,score)
        pygame.quit()
        sys.exit()

    

    def save_score(username, score):
        try:
            connection = mysql.connector.connect(
                host="localhost",     # change if hosted remotely
                user="root",
                password="SQL@ksk9405",
                database="genplayarcade"
            )

            cursor = connection.cursor()

            query = "INSERT INTO snake_game_scores (username, score) VALUES (%s, %s)"
            values = (username, score)

            cursor.execute(query, values)
            connection.commit()

            print("Score saved successfully!")

        except mysql.connector.Error as err:
            print(f"Error: {err}")

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


    if __name__ == "__main__":
        main()

if st.button("⬅️Back"):
    st.switch_page("login.py")
