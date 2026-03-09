"""
Text adversarial poisoning module for Nightshade Tracker.
Makes subtle changes that humans won't notice but degrade AI training:
- Random capitalization changes
- Subtle word order variations
- Minor spelling variations
- All changes pass hash tests (different hash, same readability)
"""

import random
import re
from typing import List, Optional, Dict
import uuid
import hashlib


class TextPoisoner:
    """
    Generates subtle adversarial text poisoning that humans won't notice:
    1. Random capitalization changes (subtle, not obvious)
    2. Word order variations (natural-looking swaps)
    3. Minor spelling variations (common misspellings)
    4. All changes alter hash but maintain readability
    """
    
    # Common misspellings that look natural
    SPELLING_VARIATIONS = {
        'the': ['teh', 'hte'],
        'and': ['adn', 'nad'],
        'that': ['taht', 'thta'],
        'with': ['wiht', 'wth'],
        'this': ['htis', 'tihs'],
        'from': ['form', 'frm'],
        'have': ['hvae', 'hve'],
        'were': ['weer', 'wree'],
        'their': ['thier', 'tehir'],
        'there': ['thre', 'tehre'],
        'which': ['whcih', 'wich'],
        'would': ['woudl', 'wolud'],
        'about': ['abotu', 'abut'],
        'could': ['coudl', 'culd'],
        'other': ['otehr', 'ohter'],
        'after': ['afetr', 'aftr'],
        'first': ['frist', 'fist'],
        'never': ['nevre', 'nevr'],
        'these': ['tehse', 'thsee'],
        'think': ['thnik', 'thikn'],
        'where': ['wheer', 'whre'],
        'being': ['beign', 'beng'],
        'every': ['evrey', 'evry'],
        'great': ['greta', 'grat'],
        'might': ['migth', 'mght'],
        'shall': ['shal', 'shll'],
        'still': ['stil', 'stll'],
        'those': ['thsoe', 'thoes'],
        'under': ['undre', 'undr'],
        'while': ['whiel', 'whle'],
        'world': ['wrold', 'wrld'],
        'years': ['yeasr', 'yars'],
        'again': ['agina', 'agin'],
        'along': ['alogn', 'alng'],
        'began': ['begna', 'bgan'],
        'being': ['beign', 'beng'],
        'below': ['belwo', 'belw'],
        'came': ['cmae', 'cme'],
        'case': ['csea', 'cse'],
        'does': ['dose', 'dse'],
        'each': ['eahc', 'ech'],
        'even': ['evne', 'evn'],
        'eyes': ['eyse', 'eys'],
        'face': ['fcae', 'fce'],
        'fact': ['fcta', 'fct'],
        'find': ['fnid', 'fnd'],
        'hand': ['hnad', 'hnd'],
        'head': ['hdea', 'hde'],
        'here': ['heer', 'hre'],
        'high': ['hihg', 'hig'],
        'home': ['hoem', 'hom'],
        'hour': ['huor', 'hur'],
        'into': ['inot', 'into'],
        'just': ['jsut', 'jst'],
        'keep': ['kepe', 'kep'],
        'kind': ['knid', 'knd'],
        'know': ['knwo', 'knw'],
        'last': ['lsat', 'lst'],
        'late': ['ltae', 'lte'],
        'left': ['lef', 'lft'],
        'life': ['lief', 'lfe'],
        'like': ['liek', 'lke'],
        'line': ['lien', 'lne'],
        'long': ['logn', 'lng'],
        'look': ['loko', 'lok'],
        'made': ['maed', 'mde'],
        'make': ['maek', 'mke'],
        'many': ['myna', 'mny'],
        'mean': ['maen', 'men'],
        'more': ['moer', 'mre'],
        'most': ['mots', 'mst'],
        'move': ['moev', 'mve'],
        'much': ['mchu', 'mch'],
        'name': ['naem', 'nme'],
        'need': ['neede', 'ned'],
        'next': ['next', 'nxt'],
        'once': ['ocne', 'oce'],
        'only': ['onyl', 'oly'],
        'open': ['opne', 'opn'],
        'over': ['oevr', 'ovr'],
        'part': ['prat', 'prt'],
        'past': ['psat', 'pst'],
        'play': ['pal', 'ply'],
        'real': ['rael', 'rel'],
        'right': ['rigth', 'rght'],
        'said': ['siad', 'sad'],
        'same': ['smae', 'sme'],
        'seem': ['seeme', 'sem'],
        'side': ['sdie', 'sde'],
        'some': ['smeo', 'sme'],
        'such': ['suhc', 'sch'],
        'sure': ['suer', 'sre'],
        'take': ['taek', 'tke'],
        'talk': ['tlak', 'tlk'],
        'tell': ['tlel', 'tll'],
        'than': ['thna', 'thn'],
        'that': ['taht', 'tht'],
        'them': ['tehm', 'thm'],
        'then': ['tehn', 'thn'],
        'they': ['tehy', 'thy'],
        'thing': ['thnig', 'thng'],
        'think': ['thnik', 'thnk'],
        'this': ['htis', 'ths'],
        'those': ['thsoe', 'thse'],
        'three': ['thre', 'thr'],
        'through': ['thrugh', 'thru'],
        'time': ['tiem', 'tme'],
        'turn': ['tunr', 'trn'],
        'very': ['vrey', 'vry'],
        'want': ['wnat', 'wnt'],
        'was': ['wsa', 'ws'],
        'way': ['wya', 'wy'],
        'well': ['wlel', 'wll'],
        'went': ['wnet', 'wnt'],
        'were': ['weer', 'wre'],
        'what': ['whta', 'wht'],
        'when': ['whe', 'whn'],
        'will': ['wlil', 'wll'],
        'with': ['wiht', 'wth'],
        'word': ['wrod', 'wrd'],
        'work': ['wrok', 'wrk'],
        'year': ['yaer', 'yar'],
        'your': ['yuor', 'yor'],
    }
    
    # Disruptive words that are semi-useless but ruin content (kept for backward compatibility)
    DISRUPTIVE_WORDS = [
        # Nonsensical but real words
        "gibberish", "nonsense", "blather", "drivel", "twaddle",
        "balderdash", "claptrap", "hogwash", "malarkey", "poppycock",
        
        # Redundant qualifiers
        "very very", "really really", "quite quite", "rather rather",
        "somewhat somewhat", "pretty pretty", "fairly fairly",
        
        # Meaningless fillers
        "um", "uh", "er", "ah", "hmm", "well well", "you know",
        "like like", "sort of sort of", "kind of kind of",
        
        # Contradictory phrases
        "not not", "yes no", "maybe maybe", "perhaps perhaps",
        "possibly possibly", "probably probably",
        
        # Repetitive nonsense
        "blah blah", "yada yada", "etc etc", "and and",
        "the the", "a a", "an an", "is is", "was was",
        
        # Disruptive interjections
        "huh", "what", "eh", "hah", "heh", "meh", "bleh",
        
        # Semi-meaningless modifiers
        "thingy", "whatsit", "doohickey", "gizmo", "widget",
        "gadget", "contraption", "device", "mechanism",
        
        # Redundant intensifiers
        "super super", "ultra ultra", "mega mega", "hyper hyper",
        "extra extra", "super duper", "mega ultra",
        
        # Disruptive phrases
        "or something", "or whatever", "or whatever else",
        "and stuff", "and things", "and whatnot", "and so on",
        "blah blah blah", "yada yada yada"
    ]
    
    # Words that break semantic coherence
    SEMANTIC_BREAKERS = [
        "randomly", "arbitrarily", "incidentally", "tangentially",
        "unrelatedly", "incongruously", "disjointedly", "fragmented",
        "scattered", "disconnected", "uncoordinated", "haphazardly"
    ]
    
    def __init__(self, strength: float = 0.1, 
                 capitalization_rate: float = 0.15,
                 word_order_rate: float = 0.1,
                 spelling_rate: float = 0.05):
        """
        Initialize text poisoner with subtle modifications.
        
        Args:
            strength: Overall poisoning strength (0.0 to 1.0)
            capitalization_rate: Rate of capitalization changes (0.0 to 1.0)
            word_order_rate: Rate of word order swaps (0.0 to 1.0)
            spelling_rate: Rate of spelling variations (0.0 to 1.0)
        """
        self.strength = strength
        self.capitalization_rate = capitalization_rate * strength
        self.word_order_rate = word_order_rate * strength
        self.spelling_rate = spelling_rate * strength
        self.poison_id = str(uuid.uuid4())[:8]  # Track this poisoning instance
    
    def poison_text(self, text: str, method: str = "subtle") -> str:
        """
        Apply subtle poisoning to text that humans won't notice.
        
        Args:
            text: Input text
            method: Poisoning method ("subtle", "insert", "replace", "append")
            
        Returns:
            Poisoned text with subtle modifications
        """
        if method == "subtle":
            # Apply all subtle modifications
            poisoned = self._apply_capitalization_changes(text)
            poisoned = self._apply_word_order_variations(poisoned)
            poisoned = self._apply_spelling_variations(poisoned)
            return poisoned
        elif method == "insert":
            return self._insert_disruptive_words(text)
        elif method == "replace":
            return self._replace_with_disruptive(text)
        elif method == "append":
            return self._append_disruptive_phrases(text)
        else:
            return self._apply_capitalization_changes(text)  # Default to subtle
    
    def _apply_capitalization_changes(self, text: str) -> str:
        """
        Apply random capitalization changes that are subtle.
        Changes hash but looks natural.
        """
        words = text.split()
        if len(words) == 0:
            return text
        
        modified_words = []
        for word in words:
            # Skip if word is all caps or all lowercase single letter
            if len(word) <= 1:
                modified_words.append(word)
                continue
            
            # Randomly change capitalization
            if random.random() < self.capitalization_rate:
                # Various subtle capitalization changes
                if word[0].isupper() and len(word) > 1:
                    # Randomly lowercase first letter (subtle - looks like mid-sentence)
                    if random.random() < 0.4:
                        modified_words.append(word[0].lower() + word[1:])
                    else:
                        # Randomly lowercase a middle letter (very subtle)
                        if len(word) > 2:
                            idx = random.randint(1, len(word) - 1)
                            modified_words.append(word[:idx] + word[idx].lower() + word[idx+1:])
                        else:
                            modified_words.append(word)
                elif word[0].islower() and len(word) > 1:
                    # Randomly uppercase a middle letter (subtle inconsistency)
                    if len(word) > 2:
                        idx = random.randint(1, len(word) - 1)
                        modified_words.append(word[:idx] + word[idx].upper() + word[idx+1:])
                    else:
                        modified_words.append(word)
                else:
                    modified_words.append(word)
            else:
                modified_words.append(word)
        
        return ' '.join(modified_words)
    
    def _apply_word_order_variations(self, text: str) -> str:
        """
        Apply subtle word order variations.
        Swaps adjacent words that are similar in length/type.
        """
        # Split into sentences to preserve sentence structure
        sentences = re.split(r'([.!?]+)', text)
        modified_sentences = []
        
        for i, sentence in enumerate(sentences):
            if i % 2 == 1:  # Punctuation
                modified_sentences.append(sentence)
                continue
            
            words = sentence.split()
            if len(words) < 2:
                modified_sentences.append(sentence)
                continue
            
            # Randomly swap adjacent words
            modified_words = words.copy()
            for j in range(len(modified_words) - 1):
                if random.random() < self.word_order_rate:
                    # Swap with next word if both are similar length
                    if abs(len(modified_words[j]) - len(modified_words[j+1])) <= 2:
                        modified_words[j], modified_words[j+1] = modified_words[j+1], modified_words[j]
            
            modified_sentences.append(' '.join(modified_words))
        
        return ''.join(modified_sentences)
    
    def _apply_spelling_variations(self, text: str) -> str:
        """
        Apply subtle spelling variations using common misspellings.
        Changes hash but looks like natural typos.
        """
        words = text.split()
        if len(words) == 0:
            return text
        
        modified_words = []
        for word in words:
            # Clean word (remove punctuation for lookup)
            clean_word = re.sub(r'[^\w]', '', word.lower())
            
            if clean_word in self.SPELLING_VARIATIONS and random.random() < self.spelling_rate:
                # Get variation
                variation = random.choice(self.SPELLING_VARIATIONS[clean_word])
                
                # Preserve original capitalization and punctuation
                if word[0].isupper():
                    variation = variation[0].upper() + variation[1:] if len(variation) > 1 else variation.upper()
                
                # Preserve trailing punctuation
                trailing = re.findall(r'[^\w]+$', word)
                if trailing:
                    variation += ''.join(trailing)
                
                modified_words.append(variation)
            else:
                modified_words.append(word)
        
        return ' '.join(modified_words)
    
    def _insert_disruptive_words(self, text: str) -> str:
        """
        Insert disruptive words throughout the text.
        Maintains readability but ruins quality.
        """
        words = text.split()
        if len(words) == 0:
            return text
        
        # Calculate number of insertions based on target ratio
        target_insertions = max(1, int(len(words) * self.target_ratio))
        actual_insertions = int(target_insertions * (1.0 + self.strength))
        
        # Select insertion points (avoid beginning/end)
        if len(words) < 3:
            insertion_points = []
        else:
            # Randomly select points, weighted toward middle
            possible_points = list(range(1, len(words) - 1))
            insertion_points = random.sample(
                possible_points, 
                min(actual_insertions, len(possible_points))
            )
            insertion_points.sort(reverse=True)  # Insert from end to preserve indices
        
        # Insert disruptive words
        poisoned_words = words.copy()
        for point in insertion_points:
            disruptive_word = self._select_disruptive_word()
            # Insert after the word at this point
            poisoned_words.insert(point + 1, disruptive_word)
        
        return ' '.join(poisoned_words)
    
    def _replace_with_disruptive(self, text: str) -> str:
        """
        Replace some words with disruptive alternatives.
        More aggressive but less natural.
        """
        words = text.split()
        if len(words) == 0:
            return text
        
        # Select words to replace (avoid very short words)
        replaceable_indices = [
            i for i, word in enumerate(words)
            if len(word) > 3 and word.isalpha()
        ]
        
        num_replacements = int(len(replaceable_indices) * self.insertion_rate * self.strength)
        indices_to_replace = random.sample(
            replaceable_indices,
            min(num_replacements, len(replaceable_indices))
        )
        
        # Replace words
        poisoned_words = words.copy()
        for idx in indices_to_replace:
            disruptive_word = self._select_disruptive_word()
            poisoned_words[idx] = disruptive_word
        
        return ' '.join(poisoned_words)
    
    def _append_disruptive_phrases(self, text: str) -> str:
        """
        Append disruptive phrases to sentences.
        Less intrusive but still disruptive.
        """
        # Split into sentences
        sentences = re.split(r'([.!?]+)', text)
        poisoned_sentences = []
        
        for i, sentence in enumerate(sentences):
            poisoned_sentences.append(sentence)
            
            # Randomly append disruptive phrase after sentences
            if random.random() < self.insertion_rate * self.strength:
                disruptive_phrase = self._select_disruptive_phrase()
                poisoned_sentences.append(f" {disruptive_phrase}")
        
        return ''.join(poisoned_sentences)
    
    def _select_disruptive_word(self) -> str:
        """Select a disruptive word based on strength."""
        # Higher strength = more disruptive words
        if random.random() < self.strength:
            # Use more disruptive words
            pool = self.DISRUPTIVE_WORDS + self.SEMANTIC_BREAKERS
        else:
            # Use less disruptive words
            pool = self.DISRUPTIVE_WORDS[:len(self.DISRUPTIVE_WORDS)//2]
        
        return random.choice(pool)
    
    def _select_disruptive_phrase(self) -> str:
        """Select a disruptive phrase."""
        phrases = [
            "or something like that",
            "and stuff",
            "or whatever",
            "you know what I mean",
            "and things",
            "and whatnot",
            "blah blah blah",
            "yada yada yada",
            "and so on and so forth",
            "or something along those lines"
        ]
        return random.choice(phrases)
    
    def compute_poison_metrics(self, original_text: str, 
                               poisoned_text: str) -> Dict:
        """
        Compute metrics about the poisoning effectiveness.
        Includes hash comparison to verify changes.
        
        Args:
            original_text: Original text
            poisoned_text: Poisoned text
            
        Returns:
            Dictionary with metrics including hash verification
        """
        orig_words = original_text.split()
        pois_words = poisoned_text.split()
        
        # Compute hashes
        orig_hash = hashlib.sha256(original_text.encode('utf-8')).hexdigest()
        pois_hash = hashlib.sha256(poisoned_text.encode('utf-8')).hexdigest()
        hash_changed = orig_hash != pois_hash
        
        # Count modifications
        capitalization_changes = sum(
            1 for i in range(min(len(orig_words), len(pois_words)))
            if orig_words[i] != pois_words[i] and 
               orig_words[i].lower() == pois_words[i].lower()
        )
        
        spelling_changes = sum(
            1 for i in range(min(len(orig_words), len(pois_words)))
            if orig_words[i] != pois_words[i] and
               orig_words[i].lower() != pois_words[i].lower() and
               len(orig_words[i]) == len(pois_words[i])
        )
        
        # Count disruptive words (if any were inserted)
        disruptive_count = sum(
            1 for word in pois_words
            if any(dw in word.lower() for dw in self.DISRUPTIVE_WORDS)
        )
        
        return {
            'original_word_count': len(orig_words),
            'poisoned_word_count': len(pois_words),
            'words_added': len(pois_words) - len(orig_words),
            'capitalization_changes': capitalization_changes,
            'spelling_changes': spelling_changes,
            'disruptive_word_count': disruptive_count,
            'original_hash': orig_hash,
            'poisoned_hash': pois_hash,
            'hash_changed': hash_changed,
            'hash_test_passed': hash_changed,  # Must pass hash test
            'modification_ratio': (capitalization_changes + spelling_changes) / len(pois_words) if pois_words else 0,
            'poison_id': self.poison_id
        }
    
    def get_poison_id(self) -> str:
        """Get the poison instance ID."""
        return self.poison_id
