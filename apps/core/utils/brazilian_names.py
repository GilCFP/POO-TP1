"""
Brazilian name datasets and utilities for generating realistic customer names.

This module contains authentic Brazilian first names and surnames based on
Brazilian census data and cultural patterns.
"""

import random


# Common Brazilian male first names
MALE_FIRST_NAMES = [
    'João', 'José', 'Antônio', 'Francisco', 'Carlos', 'Paulo', 'Pedro', 'Lucas', 'Luiz', 'Marcos',
    'Luis', 'Gabriel', 'Rafael', 'Daniel', 'Marcelo', 'Bruno', 'Eduardo', 'Felipe', 'Raimundo', 'Rodrigo',
    'Manoel', 'Nelson', 'Roberto', 'Fabio', 'Leonardo', 'Jeferson', 'Lauro', 'João Paulo', 'José Carlos',
    'Antônio Carlos', 'Marcio', 'Geraldo', 'Sérgio', 'Ricardo', 'Jorge', 'Alberto', 'Edson', 'Wesley',
    'Ronaldo', 'Francisco das Chagas', 'Danilo', 'Gilberto', 'Sidnei', 'Davi', 'Fábio', 'César',
    'Alexandre', 'Antônio José', 'Ângelo', 'Arlindo', 'Benedito', 'Cláudio', 'Cristiano', 'Diego',
    'Everton', 'Fernando', 'Gustavo', 'Henrique', 'Igor', 'Ivan', 'Jaime', 'Leandro', 'Márcio',
    'Mateus', 'Maurício', 'Mauro', 'Miguel', 'Nilson', 'Otávio', 'Patrick', 'Renan', 'Renato',
    'Robson', 'Samuel', 'Thiago', 'Vinícius', 'Wagner', 'William'
]

# Common Brazilian female first names
FEMALE_FIRST_NAMES = [
    'Maria', 'Ana', 'Francisca', 'Antônia', 'Adriana', 'Juliana', 'Márcia', 'Fernanda', 'Patricia',
    'Aline', 'Sandra', 'Camila', 'Amanda', 'Bruna', 'Jessica', 'Leticia', 'Julia', 'Luciana', 'Vanessa',
    'Marcia', 'Denise', 'Fatima', 'Simone', 'Mônica', 'Débora', 'Carolina', 'Viviane', 'Rosana',
    'Gabriela', 'Thais', 'Andrea', 'Larissa', 'Cristina', 'Carla', 'Beatriz', 'Renata', 'Raquel',
    'Sabrina', 'Joana', 'Mariana', 'Cláudia', 'Patrícia', 'Izabel', 'Cristiane', 'Michele', 'Francine',
    'Roberta', 'Misael', 'Natália', 'Bianca', 'Tatiane', 'Silvia', 'Valeria', 'Lilian', 'Priscila',
    'Kátia', 'Rosângela', 'Vera', 'Lúcia', 'Marta', 'Roseli', 'Tânia', 'Maria José', 'Maria das Graças',
    'Aparecida', 'Conceição', 'Rosário', 'Socorro', 'Dolores', 'Carmo', 'Lourdes', 'Fátima',
    'Glória', 'Vitória', 'Esperança', 'Nazaré', 'Piedade', 'Dores', 'Amparo', 'Luz', 'Paz'
]

# Common Brazilian surnames
SURNAMES = [
    'Silva', 'Santos', 'Oliveira', 'Souza', 'Rodrigues', 'Ferreira', 'Alves', 'Pereira', 'Lima', 'Gomes',
    'Ribeiro', 'Carvalho', 'Almeida', 'Lopes', 'Soares', 'Fernandes', 'Vieira', 'Barbosa', 'Rocha', 'Dias',
    'Monteiro', 'Mendes', 'Cardoso', 'Reis', 'Araújo', 'Cavalcanti', 'Dantas', 'Ramos', 'Nunes', 'Freitas',
    'Batista', 'Azevedo', 'Barros', 'Nascimento', 'Vasconcelos', 'Castro', 'Pinto', 'Farias', 'Brito', 'Correia',
    'Marques', 'Moreira', 'Teixeira', 'Morais', 'Machado', 'Campos', 'Martins', 'Torres', 'Costa', 'Pires',
    'Cunha', 'Melo', 'Fonseca', 'Moura', 'Sales', 'Andrade', 'Macedo', 'Matos', 'Coelho', 'Magalhães',
    'Paiva', 'Santana', 'Nogueira', 'Tavares', 'Miranda', 'Bezerra', 'Guimarães', 'Borges', 'Moraes', 'Lacerda',
    'Amaral', 'Duarte', 'Pacheco', 'Siqueira', 'Leite', 'Sampaio', 'Rezende', 'Menezes', 'Aguiar', 'Passos',
    'Silveira', 'Godoy', 'Peixoto', 'Camargo', 'Fagundes', 'Bispo', 'Figueiredo', 'Valente', 'Cordeiro', 'Pessoa'
]

# Double surnames (common Brazilian pattern)
DOUBLE_SURNAMES = [
    'Silva Santos', 'Santos Silva', 'Oliveira Silva', 'Silva Oliveira', 'Souza Santos', 'Santos Souza',
    'Ferreira Silva', 'Silva Ferreira', 'Alves Santos', 'Santos Alves', 'Pereira Silva', 'Silva Pereira',
    'Lima Santos', 'Santos Lima', 'Gomes Silva', 'Silva Gomes', 'Ribeiro Santos', 'Santos Ribeiro',
    'Carvalho Silva', 'Silva Carvalho', 'Almeida Santos', 'Santos Almeida', 'Lopes Silva', 'Silva Lopes',
    'Soares Santos', 'Santos Soares', 'Fernandes Silva', 'Silva Fernandes', 'Vieira Santos', 'Santos Vieira',
    'Barbosa Silva', 'Silva Barbosa', 'Rocha Santos', 'Santos Rocha', 'Dias Silva', 'Silva Dias'
]


def generate_male_name():
    """
    Generate a realistic Brazilian male name.
    
    Returns:
        str: Full name with first name and surname(s)
    """
    first_name = random.choice(MALE_FIRST_NAMES)
    
    # 30% chance of double surname, 70% single surname
    if random.random() < 0.3:
        surname = random.choice(DOUBLE_SURNAMES)
    else:
        surname = random.choice(SURNAMES)
    
    return f"{first_name} {surname}"


def generate_female_name():
    """
    Generate a realistic Brazilian female name.
    
    Returns:
        str: Full name with first name and surname(s)
    """
    first_name = random.choice(FEMALE_FIRST_NAMES)
    
    # 30% chance of double surname, 70% single surname
    if random.random() < 0.3:
        surname = random.choice(DOUBLE_SURNAMES)
    else:
        surname = random.choice(SURNAMES)
    
    return f"{first_name} {surname}"


def generate_random_name():
    """
    Generate a random Brazilian name (male or female).
    
    Returns:
        str: Full name with first name and surname(s)
    """
    if random.choice([True, False]):
        return generate_male_name()
    else:
        return generate_female_name()


def generate_name_by_gender(gender):
    """
    Generate a Brazilian name for a specific gender.
    
    Args:
        gender (str): 'M' for male, 'F' for female
        
    Returns:
        str: Full name appropriate for the specified gender
        
    Raises:
        ValueError: If gender is not 'M' or 'F'
    """
    if gender.upper() == 'M':
        return generate_male_name()
    elif gender.upper() == 'F':
        return generate_female_name()
    else:
        raise ValueError("Gender must be 'M' for male or 'F' for female")


def get_first_name_by_gender(gender):
    """
    Get a random first name for a specific gender.
    
    Args:
        gender (str): 'M' for male, 'F' for female
        
    Returns:
        str: First name appropriate for the specified gender
        
    Raises:
        ValueError: If gender is not 'M' or 'F'
    """
    if gender.upper() == 'M':
        return random.choice(MALE_FIRST_NAMES)
    elif gender.upper() == 'F':
        return random.choice(FEMALE_FIRST_NAMES)
    else:
        raise ValueError("Gender must be 'M' for male or 'F' for female")


def get_random_surname():
    """
    Get a random Brazilian surname.
    
    Returns:
        str: A single surname or double surname
    """
    # 30% chance of double surname, 70% single surname
    if random.random() < 0.3:
        return random.choice(DOUBLE_SURNAMES)
    else:
        return random.choice(SURNAMES)