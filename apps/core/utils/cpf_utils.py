"""
CPF (Cadastro de Pessoas Físicas) utilities for Brazilian tax ID generation and validation.

This module provides functions to generate valid CPF numbers, validate existing CPF numbers,
and format CPF numbers for display according to Brazilian standards.
"""

import random
import re


def validate_cpf(cpf):
    """
    Validate a CPF number using the official Brazilian algorithm.
    
    Args:
        cpf (str): CPF number to validate (can include formatting)
        
    Returns:
        bool: True if CPF is valid, False otherwise
    """
    # Remove any non-digit characters
    cpf = re.sub(r'\D', '', cpf)
    
    # CPF must have exactly 11 digits
    if len(cpf) != 11:
        return False
    
    # CPF cannot be all the same digit
    if cpf == cpf[0] * 11:
        return False
    
    # Calculate first verification digit
    sum1 = 0
    for i in range(9):
        sum1 += int(cpf[i]) * (10 - i)
    
    remainder1 = sum1 % 11
    digit1 = 0 if remainder1 < 2 else 11 - remainder1
    
    # Check first verification digit
    if int(cpf[9]) != digit1:
        return False
    
    # Calculate second verification digit
    sum2 = 0
    for i in range(10):
        sum2 += int(cpf[i]) * (11 - i)
    
    remainder2 = sum2 % 11
    digit2 = 0 if remainder2 < 2 else 11 - remainder2
    
    # Check second verification digit
    if int(cpf[10]) != digit2:
        return False
    
    return True


def generate_cpf():
    """
    Generate a valid CPF number using the official Brazilian algorithm.
    
    Returns:
        str: A valid 11-digit CPF number (without formatting)
    """
    # Generate first 9 digits randomly
    cpf_digits = [random.randint(0, 9) for _ in range(9)]
    
    # Calculate first verification digit
    sum1 = 0
    for i in range(9):
        sum1 += cpf_digits[i] * (10 - i)
    
    remainder1 = sum1 % 11
    digit1 = 0 if remainder1 < 2 else 11 - remainder1
    cpf_digits.append(digit1)
    
    # Calculate second verification digit
    sum2 = 0
    for i in range(10):
        sum2 += cpf_digits[i] * (11 - i)
    
    remainder2 = sum2 % 11
    digit2 = 0 if remainder2 < 2 else 11 - remainder2
    cpf_digits.append(digit2)
    
    # Convert to string
    return ''.join(map(str, cpf_digits))


def format_cpf(cpf):
    """
    Format a CPF number for display with standard Brazilian formatting.
    
    Args:
        cpf (str): CPF number (11 digits, with or without formatting)
        
    Returns:
        str: Formatted CPF in the pattern XXX.XXX.XXX-XX
        
    Raises:
        ValueError: If CPF doesn't have exactly 11 digits
    """
    # Remove any non-digit characters
    cpf_clean = re.sub(r'\D', '', cpf)
    
    if len(cpf_clean) != 11:
        raise ValueError("CPF must have exactly 11 digits")
    
    # Format as XXX.XXX.XXX-XX
    return f"{cpf_clean[:3]}.{cpf_clean[3:6]}.{cpf_clean[6:9]}-{cpf_clean[9:]}"


def clean_cpf(cpf):
    """
    Remove formatting from a CPF number, keeping only digits.
    
    Args:
        cpf (str): CPF number with or without formatting
        
    Returns:
        str: CPF number with only digits
    """
    return re.sub(r'\D', '', cpf)


def generate_valid_cpf_formatted():
    """
    Generate a valid CPF number with standard Brazilian formatting.
    
    Returns:
        str: A valid formatted CPF in the pattern XXX.XXX.XXX-XX
    """
    cpf = generate_cpf()
    return format_cpf(cpf)