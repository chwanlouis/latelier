import re
from utlities.download_book_escoffier import escoffier_file_path


class EscoffierBookParser(object):
    @staticmethod
    def read_book():
        with open(escoffier_file_path, 'r', encoding='utf-8') as f:
            book_content = f.read()
            return book_content

    @staticmethod
    def split_book_into_recipes(book_content: str) -> dict:
        recipe_title_pattern = re.compile(r'^\d+—[^\n]*', re.MULTILINE)
        chapter_pattern = re.compile(r'^CHAPTER [IVXLCDM]+\s', re.MULTILINE)
        matches = list()
        for match in recipe_title_pattern.finditer(book_content):
            matches.append({'start': match.start(), 'end': match.end(), 'title': match.group(0).strip()})

        recipes = dict()
        for i, match_info in enumerate(matches):
            start_index = match_info['start']
            title = match_info['title']
            if i + 1 < len(matches):
                next_recipe_start = matches[i + 1]['start']
            else:
                next_recipe_start = len(book_content)
            end_index = next_recipe_start
            chapter_match = chapter_pattern.search(book_content, start_index + len(title), next_recipe_start)
            if chapter_match:
                end_index = min(end_index, chapter_match.start())
            recipe_text = book_content[start_index:end_index].strip()
            recipes[title] = recipe_text
        return recipes

    @staticmethod
    def extract_cooking_techniques_deepseek(recipe_text: str) -> list:
        system_prompt = ("Extract the cooking techniques used in the following recipe."
                         "Return a list of techniques, without duplicates.")
        prompt = f"{system_prompt}\n\nRecipe:\n{recipe_text}"

    def main(self):
        book_content = self.read_book()
        recipes = self.split_book_into_recipes(book_content)
        for title, recipe in recipes.items():
            print(f"Title: {title}\nRecipe:\n{recipe[:200]}...\n{'-'*80}\n")


if __name__ == "__main__":
    parser = EscoffierBookParser()
    parser.main()