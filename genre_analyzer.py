"""
Simple Genre Analysis Tool for RuneScape Wiki Pages

Analyzes wikitext content to answer genre analysis questions systematically.
"""

import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List


class GenreAnalyzer:
    """Analyzes RuneScape Wiki pages for genre characteristics."""
    
    def __init__(self, data_file: str = "assets/runescape_top100.json"):
        self.data_file = data_file
        self.pages = []
        self.load_data()
    
    def load_data(self):
        """Load wiki pages from JSON file."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.pages = json.load(f)
            print(f"Loaded {len(self.pages)} pages for analysis")
        except FileNotFoundError:
            print(f"Data file {self.data_file} not found. Run main.py first to fetch data.")
            self.pages = []
    
    def check_cache(self) -> bool:
        """Check if cached data exists and is recent enough."""
        if not self.pages:
            return False
        
        # Check if we have a reasonable amount of data
        if len(self.pages) < 50:
            print(f"Only {len(self.pages)} pages in cache. Consider fetching more data.")
            return False
        
        print(f"Using cached data with {len(self.pages)} pages.")
        return True
    
    def clean_wikitext(self, text: str) -> str:
        """Clean wikitext by removing markup and keeping readable content."""
        # Remove wiki markup
        text = re.sub(r'\[\[([^|\]]+)(\|[^\]]+)?\]\]', r'\1', text)  # [[link|display]] -> display
        text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)  # [[link]] -> link
        text = re.sub(r'\{\{[^}]*\}\}', '', text)  # Remove templates {{...}}
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        text = re.sub(r'==+', '', text)  # Remove section headers
        text = re.sub(r'\*+', '', text)  # Remove list markers
        text = re.sub(r'#+', '', text)  # Remove numbered list markers
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        return text.strip()
    
    def extract_structural_features(self) -> Dict:
        """Analyze structural patterns in the pages."""
        features = {
            'common_sections': Counter(),
            'common_templates': Counter(),
            'avg_page_length': 0
        }
        
        total_words = 0
        total_pages = len(self.pages)
        
        for page in self.pages:
            text = page.get('wikitext', '')
            cleaned = self.clean_wikitext(text)
            
            # Count words
            words = cleaned.split()
            total_words += len(words)
            
            # Extract sections (== Header ==)
            sections = re.findall(r'==+([^=]+)==+', text)
            for section in sections:
                features['common_sections'][section.strip().lower()] += 1
            
            # Extract templates {{Template}}
            templates = re.findall(r'\{\{([^}]+)\}\}', text)
            for template in templates:
                template_name = template.split('|')[0].strip()
                features['common_templates'][template_name] += 1
        
        features['avg_page_length'] = total_words / total_pages if total_pages > 0 else 0
        
        return features
    
    def analyze_language_patterns(self) -> Dict:
        """Analyze language and style conventions, focusing on game-specific terms."""
        all_text = ""
        word_freq = Counter()
        
        # Common English words to filter out
        common_words = {
            'the', 'and', 'can', 'from', 'with', 'added', 'history', 'for', 'update', 'that',
            'are', 'player', 'this', 'will', 'was', 'have', 'white', 'when', 'they', 'has',
            'you', 'your', 'all', 'but', 'not', 'use', 'get', 'one', 'two', 'three', 'four',
            'five', 'six', 'seven', 'eight', 'nine', 'ten', 'first', 'second', 'third',
            'last', 'new', 'old', 'good', 'bad', 'big', 'small', 'high', 'low', 'long',
            'short', 'fast', 'slow', 'easy', 'hard', 'more', 'less', 'most', 'least',
            'some', 'any', 'all', 'each', 'every', 'other', 'another', 'same', 'different',
            'time', 'day', 'night', 'year', 'month', 'week', 'hour', 'minute', 'second',
            'place', 'way', 'thing', 'part', 'kind', 'sort', 'type', 'form', 'shape',
            'size', 'color', 'red', 'blue', 'green', 'yellow', 'black', 'brown', 'gray',
            'make', 'made', 'do', 'did', 'done', 'go', 'went', 'gone', 'come', 'came',
            'see', 'saw', 'seen', 'look', 'looked', 'find', 'found', 'take', 'took', 'taken',
            'give', 'gave', 'given', 'put', 'set', 'get', 'got', 'gotten', 'know', 'knew',
            'known', 'think', 'thought', 'say', 'said', 'tell', 'told', 'ask', 'asked',
            'work', 'worked', 'help', 'helped', 'try', 'tried', 'turn', 'turned',
            'move', 'moved', 'play', 'played', 'run', 'ran', 'walk', 'walked',
            'sit', 'sat', 'stand', 'stood', 'lie', 'lay', 'lain', 'sleep', 'slept',
            'eat', 'ate', 'eaten', 'drink', 'drank', 'drunk', 'buy', 'bought', 'sell', 'sold',
            'pay', 'paid', 'cost', 'spend', 'spent', 'save', 'saved', 'lose', 'lost',
            'win', 'won', 'beat', 'beaten', 'fight', 'fought', 'kill', 'killed',
            'die', 'died', 'dead', 'death', 'life', 'live', 'lived', 'alive',
            'love', 'loved', 'like', 'liked', 'hate', 'hated', 'want', 'wanted',
            'need', 'needed', 'must', 'should', 'could', 'would', 'might', 'may',
            'shall', 'will', 'do', 'does', 'did', 'have', 'has', 'had', 'be', 'am',
            'is', 'are', 'was', 'were', 'been', 'being', 'a', 'an', 'the', 'and',
            'or', 'but', 'if', 'then', 'else', 'because', 'so', 'very', 'much', 'many',
            'some', 'any', 'all', 'no', 'none', 'nothing', 'something', 'everything',
            'someone', 'anyone', 'everyone', 'nobody', 'somebody', 'anybody', 'everybody',
            'somewhere', 'anywhere', 'everywhere', 'nowhere', 'here', 'there', 'where',
            'when', 'why', 'how', 'what', 'which', 'who', 'whom', 'whose', 'yes', 'no',
            'true', 'false', 'right', 'wrong', 'correct', 'incorrect', 'yes', 'no',
            # Additional common words to filter out
            'their', 'during', 'after', 'now', 'using', 'only', 'also', 'its', 'into',
            'while', 'his', 'her', 'him', 'she', 'he', 'we', 'us', 'our', 'ours',
            'them', 'they', 'theirs', 'themselves', 'himself', 'herself', 'itself',
            'myself', 'yourself', 'yourselves', 'ourselves', 'oneself'
        }
        
        for page in self.pages:
            text = page.get('wikitext', '')
            cleaned = self.clean_wikitext(text)
            all_text += " " + cleaned
        
        # Extract words and filter out common English words
        words = all_text.lower().split()
        filtered_words = [
            w for w in words 
            if w.isalpha() and len(w) > 2 and w not in common_words
        ]
        
        # Word frequency
        word_freq = Counter(filtered_words)
        
        return {
            'most_common_words': word_freq.most_common(100),
            'vocabulary_size': len(set(filtered_words)),
            'total_words': len(filtered_words),
            'game_specific_terms': word_freq.most_common(200)
        }
    
    def identify_genre_moves(self) -> List[str]:
        """Identify common rhetorical moves in the pages."""
        moves = []
        
        for page in self.pages:
            text = page.get('wikitext', '')
            title = page.get('title', '')
            
            # Identify common moves based on content patterns
            if 'Infobox' in text:
                moves.append('define_item')
            if '== History ==' in text or '== Background ==' in text:
                moves.append('provide_context')
            if '== Stats ==' in text or '== Requirements ==' in text:
                moves.append('specify_mechanics')
            if '== Trivia ==' in text or '== Notes ==' in text:
                moves.append('add_interesting_details')
            if '== See also ==' in text:
                moves.append('connect_related_content')
            if '{{External' in text:
                moves.append('reference_other_sources')
            if '== Gallery ==' in text:
                moves.append('show_visual_evidence')
            if '== References ==' in text:
                moves.append('cite_sources')
        
        return list(set(moves))
    
    def analyze_slang_terms(self) -> Dict:
        """Identify slang/abbreviations from the RuneScape slang dictionary."""
        # Comprehensive slang terms from the Old School RuneScape slang dictionary
        slang_terms = {
            # Game-specific terms only (no common English words)
            'stats', 'combat', 'quest', 'armour', 'magic', 'experience', 'level', 'players',
            'world', 'item', 'amulet', 'patch', 'special', 'creation', 'armies', 'sack',
            'stone', 'christmas', 'knights', 'present',
            # Game-specific terms
            'runescape', 'osrs', 'rs', 'rs3', 'f2p', 'p2p', 'members', 'free', 'premium',
            'wilderness', 'wildy', 'wild', 'pvp', 'pvm', 'skilling', 'training', 'grinding',
            'xp', 'exp', 'experience', 'levels', 'skills', 'combat', 'attack', 'strength',
            'defence', 'ranged', 'prayer', 'magic', 'runecrafting', 'construction', 'hitpoints',
            'agility', 'herblore', 'thieving', 'crafting', 'fletching', 'slayer', 'hunter',
            'mining', 'smithing', 'fishing', 'cooking', 'firemaking', 'woodcutting', 'farming',
            # Equipment and items
            'armour', 'weapon', 'sword', 'bow', 'crossbow', 'staff', 'wand', 'shield',
            'helmet', 'platebody', 'platelegs', 'boots', 'gloves', 'cape', 'amulet', 'ring',
            'food', 'potion', 'prayer', 'prayers', 'spell', 'spells', 'rune', 'runes',
            # Locations and areas
            'lumbridge', 'varrock', 'falador', 'taverley', 'burthorpe', 'edgeville', 'al kharid',
            'duel arena', 'castle wars', 'clan wars', 'barbarian assault', 'pest control',
            'trouble brewing', 'fist of guthix', 'soul wars', 'stealing creation',
            # Bosses and NPCs
            'kbd', 'king black dragon', 'kq', 'kalphite queen', 'corp', 'corporeal beast',
            'jad', 'tzhaar', 'zulrah', 'vorkath', 'cerberus', 'abyssal sire', 'alchemical hydra',
            'nightmare', 'phosani', 'nex', 'arch glacor', 'kerapac', 'zuriel', 'statius',
            'vesta', 'morrigan', 'ancient', 'dragon', 'dragonfire', 'dragonfire shield',
            # Skills and training
            'tick', 'ticking', 'tick manipulation', 'efficient', 'efficiency', 'afk',
            'click intensive', 'semi afk', 'full afk', 'bank standing', 'bankstanding',
            'power training', 'powerleveling', 'powerlevelling', 'pure', 'pures', 'zerker',
            'zerkers', 'berserker', 'berserkers', 'main', 'mains', 'alt', 'alts', 'ironman',
            'ironmen', 'hardcore', 'ultimate', 'group', 'gim', 'gims', 'group ironman',
            # Combat and PvP
            'pk', 'pking', 'pker', 'pkers', 'pked', 'pked', 'loot', 'looting', 'looted',
            'risk', 'risking', 'risked', 'safe', 'safing', 'safed', 'tele', 'teles', 'teleport',
            'teleporting', 'teleported', 'escape', 'escaping', 'escaped', 'tank', 'tanking',
            'tanked', 'dps', 'damage', 'hits', 'hitting', 'hit', 'miss', 'missed', 'missing',
            'spec', 'specs', 'special', 'specials', 'specing', 'speced', 'speced', 'specing',
            # Economy and trading
            'ge', 'grand exchange', 'trade', 'trading', 'traded', 'buy', 'buying', 'bought',
            'sell', 'selling', 'sold', 'price', 'prices', 'pricing', 'priced', 'value',
            'valuing', 'valued', 'worth', 'worthless', 'valuable', 'profit', 'profitable',
            'loss', 'losing', 'lost', 'money', 'cash', 'coins', 'gp', 'gold', 'gold pieces',
            'wealth', 'rich', 'poor', 'broke', 'bankrupt', 'merchant', 'merchants', 'merching',
            'merched', 'flip', 'flipping', 'flipped', 'invest', 'investing', 'invested',
            # Clans and social
            'clan', 'clans', 'clan chat', 'cc', 'friends', 'friend', 'friended', 'unfriend',
            'unfriended', 'block', 'blocked', 'unblock', 'unblocked', 'ignore', 'ignored',
            'unignore', 'unignored', 'report', 'reported', 'reporting', 'reports',
            # Quests and achievements
            'quest', 'quests', 'questing', 'quested', 'quest cape', 'quest point cape',
            'achievement', 'achievements', 'achievement diary', 'diaries', 'diary',
            'completionist', 'completionist cape', 'trimmed', 'trimmed cape',
            # Minigames and activities
            'minigame', 'minigames', 'activity', 'activities', 'distraction', 'diversion',
            'barbarian assault', 'pest control', 'trouble brewing', 'fist of guthix',
            'soul wars', 'stealing creation', 'clan wars', 'duel arena', 'castle wars',
            # Technical terms
            'tick', 'ticks', 'ticking', 'ticked', 'game tick', 'server tick', 'client tick',
            'lag', 'lagging', 'lagged', 'dc', 'disconnect', 'disconnected', 'disconnecting',
            'crash', 'crashed', 'crashes', 'crashing', 'freeze', 'froze', 'frozen',
            'stuck', 'sticking', 'sticked', 'glitch', 'glitched', 'glitching', 'bug',
            'bugged', 'bugging', 'exploit', 'exploited', 'exploiting', 'abuse', 'abused',
            'abusing', 'macro', 'macros', 'macroing', 'macroed', 'bot', 'bots', 'botting',
            'botted', 'auto', 'automated', 'automation', 'script', 'scripts', 'scripting',
            'scripted', 'cheat', 'cheated', 'cheating', 'cheats', 'hack', 'hacked',
            'hacking', 'hacks', 'hacker', 'hackers', 'mod', 'mods', 'moderator', 'moderators',
            'admin', 'admins', 'administrator', 'administrators', 'jmod', 'jmods', 'jagex',
            'jagex moderator', 'jagex moderators', 'customer support', 'support',
            # Common abbreviations
            'lol', 'lmao', 'lmfao', 'rofl', 'roflmao', 'wtf', 'omg', 'omfg', 'fml',
            'smh', 'tbh', 'imo', 'imho', 'btw', 'fyi', 'irl', 'irl', 'irl', 'irl',
            'ty', 'thanks', 'thank you', 'np', 'no problem', 'yw', 'you welcome',
            'gl', 'good luck', 'hf', 'have fun', 'gg', 'good game', 'wp', 'well played',
            'gz', 'gratz', 'congrats', 'congratulations', 'grats', 'gratz', 'gratz',
            'rip', 'rest in peace', 'f', 'press f', 'press f to pay respects',
            'o7', 'salute', 'saluting', 'saluted', 'o/', 'wave', 'waving', 'waved',
            'xd', 'xd', 'xd', 'xd', 'xd', 'xd', 'xd', 'xd', 'xd', 'xd',
            'lul', 'lulz', 'lel', 'lels', 'kek', 'kekw', 'kekl', 'kekd', 'keked',
            'pog', 'poggers', 'pogchamp', 'pogchamp', 'pogchamp', 'pogchamp',
            'monka', 'monkas', 'monkaw', 'monkal', 'monkad', 'monkaed', 'monkaed',
            'pepe', 'pepes', 'pepega', 'pepega', 'pepega', 'pepega', 'pepega',
            'omegalul', 'omegalul', 'omegalul', 'omegalul', 'omegalul', 'omegalul',
            '4head', '4head', '4head', '4head', '4head', '4head', '4head', '4head',
            '5head', '5head', '5head', '5head', '5head', '5head', '5head', '5head',
            'omegalul', 'omegalul', 'omegalul', 'omegalul', 'omegalul', 'omegalul',
            'poggers', 'poggers', 'poggers', 'poggers', 'poggers', 'poggers',
            'monkas', 'monkas', 'monkas', 'monkas', 'monkas', 'monkas', 'monkas',
            'pepega', 'pepega', 'pepega', 'pepega', 'pepega', 'pepega', 'pepega',
            'omegalul', 'omegalul', 'omegalul', 'omegalul', 'omegalul', 'omegalul',
            '4head', '4head', '4head', '4head', '4head', '4head', '4head', '4head',
            '5head', '5head', '5head', '5head', '5head', '5head', '5head', '5head'
        }
        
        all_text = ""
        for page in self.pages:
            text = page.get('wikitext', '')
            cleaned = self.clean_wikitext(text)
            all_text += " " + cleaned
        
        words = all_text.lower().split()
        found_slang = Counter()
        
        for word in words:
            if word in slang_terms:
                found_slang[word] += 1
        
        return {
            'slang_found': dict(found_slang.most_common(40)),
            'total_slang_instances': sum(found_slang.values()),
            'unique_slang_terms': len(found_slang)
        }
    
    def generate_analysis_report(self) -> str:
        """Generate a comprehensive genre analysis report."""
        if not self.pages:
            return "No data available for analysis. Run main.py first to fetch wiki pages."
        
        structural = self.extract_structural_features()
        language = self.analyze_language_patterns()
        slang = self.analyze_slang_terms()
        moves = self.identify_genre_moves()
        
        report = f"""
# RuneScape Wiki Genre Analysis Report

## Genre Identification
**Genre:** Game Wiki Article/Encyclopedia Entry
**Purpose:** Informational reference for game players seeking specific details about game elements

## Rhetorical Situation
**Where it appears:** RuneScape Wiki (runescape.wiki)
**Who writes:** Game community members, wiki editors
**Who reads:** RuneScape players seeking information
**Purpose:** Provide comprehensive, factual information about game elements
**Discourse community values:** Accuracy, completeness, helpfulness to players

## Structural Features
- **Average page length:** {structural['avg_page_length']:.0f} words
- **Most common sections:** {', '.join([f"{k} ({v})" for k, v in structural['common_sections'].most_common(10)])}

## Language/Style Conventions
- **Game-specific vocabulary size:** {language['vocabulary_size']} unique terms
- **Total game-specific words analyzed:** {language['total_words']}

## Slang/Community Terms Analysis
- **Total slang instances found:** {slang['total_slang_instances']}
- **Unique slang terms found:** {slang['unique_slang_terms']}
- **Top 40 slang terms:** {', '.join([f"{word} ({count})" for word, count in list(slang['slang_found'].items())[:40]])}

## Common Rhetorical Moves
{', '.join(moves)}

## Modalities
- **Language:** Primary modality, highly technical and specific
- **Images:** Referenced through [[File:]] markup
- **Structure:** Hierarchical with clear sections
- **Links:** Extensive internal linking between related concepts

## Key Findings
1. **Highly structured:** Consistent use of templates and sections
2. **Technical vocabulary:** Game-specific terminology dominates
3. **Reference-oriented:** Heavy use of citations and external links
4. **Community-driven:** Collaborative editing with standardized formats
5. **Player-focused:** Content organized for practical player use

## Reflection Questions for Further Analysis
1. How does the technical vocabulary reflect the gaming community's shared knowledge?
2. What does the heavy use of templates reveal about the need for consistency?
3. How do the structural patterns serve both new and experienced players?
4. What values are reflected in the emphasis on accuracy and completeness?
"""
        return report
    
    def save_report(self, output_file: str = "genre_analysis_report.md"):
        """Save the analysis report to a markdown file."""
        report = self.generate_analysis_report()
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Genre analysis report saved to {output_file}")


def main():
    """Run the genre analysis."""
    analyzer = GenreAnalyzer()
    analyzer.save_report()
    print("\n" + "="*50)
    print(analyzer.generate_analysis_report())


if __name__ == "__main__":
    main()
