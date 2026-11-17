<?php

// PHP-CS-Fixer sur le PHP de web/ : web/tools/run.sh vendor/bin/php-cs-fixer check
$finder = (new PhpCsFixer\Finder())
    ->in(__DIR__)
    ->exclude(['vendor', 'tools']);

return (new PhpCsFixer\Config())
    ->setCacheFile(__DIR__ . '/vendor/.php-cs-fixer.cache')
    ->setRiskyAllowed(false)
    // PSR-12, moins les règles que le code ne suit pas encore : la dette, à rendre une par une
    // (retirer la ligne, puis web/tools/run.sh vendor/bin/php-cs-fixer fix).
    ->setRules([
        '@PSR12' => true,
        'statement_indentation' => false,
        'braces_position' => false,
        'single_blank_line_at_eof' => false,
        'blank_line_after_opening_tag' => false,
        'method_argument_space' => false,
        'control_structure_braces' => false,
        'single_space_around_construct' => false,
        'no_trailing_whitespace' => false,
        'function_declaration' => false,
        'binary_operator_spaces' => false,
        'spaces_inside_parentheses' => false,
        'no_whitespace_in_blank_line' => false,
        'class_definition' => false,
        'no_multiple_statements_per_line' => false,
        'no_closing_tag' => false,
        'full_opening_tag' => false,
    ])
    ->setFinder($finder);
