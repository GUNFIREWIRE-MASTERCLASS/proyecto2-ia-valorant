% =============================================================================
% UNIVERSIDAD ANDRÉS BELLO - CINF103: FUNDAMENTOS DE INTELIGENCIA ARTIFICIAL
% PROYECTO N°2: CHATBOT INTERACTIVO DE VALORANT
% =============================================================================

% -----------------------------------------------------------------------------
% 1. BASE DE CONOCIMIENTO (HECHOS)
% -----------------------------------------------------------------------------
rol(jett,      duelista).
rol(reyna,     duelista).
rol(raze,      duelista).
rol(omen,      controlador).
rol(brimstone, controlador).
rol(sova,      iniciador).
rol(fade,      iniciador).
rol(sage,      centinela).
rol(killjoy,   centinela).
rol(cypher,    centinela).

costo_kit(jett,      450).
costo_kit(reyna,     500).
costo_kit(raze,      600).
costo_kit(omen,      400).
costo_kit(brimstone, 500).
costo_kit(sova,      400).
costo_kit(fade,      600).
costo_kit(sage,      700).
costo_kit(killjoy,   600).
costo_kit(cypher,    600).

tipo_arma(classic,   pistola).
tipo_arma(frenzy,    pistola).
tipo_arma(ghost,     pistola).
tipo_arma(sheriff,   pistola).
tipo_arma(spectre,   subfusil).
tipo_arma(judge,     escopeta).
tipo_arma(bulldog,   rifle).
tipo_arma(phantom,   rifle).
tipo_arma(vandal,    rifle).
tipo_arma(operator,  francotirador).

costo(classic,        0).
costo(frenzy,       450).
costo(ghost,        500).
costo(sheriff,      800).
costo(spectre,     1600).
costo(judge,       1850).
costo(bulldog,     2050).
costo(phantom,     2900).
costo(vandal,      2900).
costo(operator,    4700).

costo(escudo_ligero,  400).
costo(escudo_pesado, 1000).

alcance_optimo(classic,   corta).
alcance_optimo(frenzy,    corta).
alcance_optimo(judge,     corta).
alcance_optimo(spectre,   media).
alcance_optimo(ghost,     media).
alcance_optimo(phantom,   media).
alcance_optimo(sheriff,   larga).
alcance_optimo(bulldog,   larga).
alcance_optimo(vandal,    larga).
alcance_optimo(operator,  larga).

% -----------------------------------------------------------------------------
% 2. REGLAS LÓGICAS Y DE INFERENCIA
% -----------------------------------------------------------------------------
creditos_validos(Creditos) :-
    integer(Creditos),
    Creditos >= 0,
    Creditos =< 9000.

mismo_rol(X, Y) :-
    rol(X, R),
    rol(Y, R),
    X \= Y.

tipo_ronda(Creditos, eco) :-
    creditos_validos(Creditos),
    Creditos < 2000, !.
tipo_ronda(Creditos, semi_buy) :-
    creditos_validos(Creditos),
    Creditos >= 2000,
    Creditos < 3900, !.
tipo_ronda(Creditos, full_buy) :-
    creditos_validos(Creditos),
    Creditos >= 3900,
    Creditos =< 9000, !.

gasto_utilidad(_, eco, 0) :- !.
gasto_utilidad(Agente, semi_buy, Gasto) :-
    costo_kit(Agente, Total),
    Gasto is round(Total / 2), !.
gasto_utilidad(Agente, full_buy, Total) :-
    costo_kit(Agente, Total), !.
gasto_utilidad(_, _, 0).

alcanza(Creditos, Arma, Escudo) :-
    creditos_validos(Creditos),
    costo(Arma, CA),
    costo(Escudo, CE),
    Total is CA + CE,
    Creditos >= Total.

arma_viable(Creditos, Distancia, Arma) :-
    creditos_validos(Creditos),
    costo(Arma, CA),
    CA =< Creditos,
    alcance_optimo(Arma, Distancia).

escudo_recomendado(Saldo, escudo_pesado) :- Saldo >= 1000, !.
escudo_recomendado(Saldo, escudo_ligero) :- Saldo >= 400, Saldo < 1000, !.
escudo_recomendado(_,     ninguno).

recomendar_plan(Creditos, Agente, Distancia, TipoRonda, Arma, GastoHab, Escudo, Resto) :-
    tipo_ronda(Creditos, TipoRonda),
    gasto_utilidad(Agente, TipoRonda, GastoHab),
    SaldoArma is Creditos - GastoHab,
    (   TipoRonda == full_buy
    ->  ( Distancia == larga -> Arma = vandal ; Arma = phantom )
    ;   TipoRonda == semi_buy
    ->  ( Distancia == larga -> Arma = bulldog ; Arma = spectre )
    ;   ( Distancia == larga -> Arma = sheriff ; Arma = classic )
    ),
    costo(Arma, CostoA),
    SaldoEscudo is SaldoArma - CostoA,
    escudo_recomendado(SaldoEscudo, Escudo),
    ( Escudo == ninguno -> CostoE = 0 ; costo(Escudo, CostoE) ),
    Resto is SaldoEscudo - CostoE.

% -----------------------------------------------------------------------------
% 3. PARSER DE FRASES
% -----------------------------------------------------------------------------
tokenizar(Texto, Palabras) :-
    string_lower(Texto, Min),
    string_chars(Min, Cs),
    maplist(limpiar_char, Cs, Cs2),
    string_chars(Limpio, Cs2),
    split_string(Limpio, " ", "", Partes),
    exclude(==(""), Partes, Limpias),
    maplist(atom_string, Palabras, Limpias).

limpiar_char(C, L) :-
    sin_tilde(C, C1),
    ( (C1 == '_' ; char_type(C1, alnum)) -> L = C1 ; L = ' ' ).

sin_tilde('á', a) :- !.
sin_tilde('é', e) :- !.
sin_tilde('í', i) :- !.
sin_tilde('ó', o) :- !.
sin_tilde('ú', u) :- !.
sin_tilde(C, C).

extraer_numero([P|_], N) :- atom_number(P, N), integer(N), !.
extraer_numero([_|Resto], N) :- extraer_numero(Resto, N).

extraer_agente([P|_], P) :- rol(P, _), !.
extraer_agente([_|Resto], Agente) :- extraer_agente(Resto, Agente).

extraer_arma([P|_], P) :- costo(P, _), P \= escudo_ligero, P \= escudo_pesado, !.
extraer_arma([_|Resto], Arma) :- extraer_arma(Resto, Arma).

extraer_distancia(Ps, larga) :- ( member(larga, Ps) ; member(lejos, Ps) ), !.
extraer_distancia(Ps, corta) :- ( member(corta, Ps) ; member(cerca, Ps) ), !.
extraer_distancia(_, corta).

% -----------------------------------------------------------------------------
% 4. RESPUESTA A INTENCIONES (Todas las cláusulas de responder/1 juntas)
% -----------------------------------------------------------------------------
responder(Ps) :-
    ( member(ayuda, Ps) ; member(help, Ps) ), !,
    mostrar_ayuda.

responder(Ps) :-
    ( member(hola, Ps) ; member(buenas, Ps) ), !,
    writeln('Bot: Hola! Preguntame sobre compras, armas, agentes o precios en Valorant.').

% ¿Qué tipo o categoría de arma es X?
responder(Ps) :-
    ( member(tipo, Ps) ; member(categoria, Ps) ; member(clase, Ps) ),
    extraer_arma(Ps, Arma), !,
    tipo_arma(Arma, Categoria),
    alcance_optimo(Arma, Rango),
    format('Bot: La ~w es un arma de tipo ~w y su alcance optimo es a distancia ~w.~n', [Arma, Categoria, Rango]).

% ¿Cuál es el rol de un agente o quiénes lo comparten?
responder(Ps) :-
    ( member(rol, Ps) ; member(comparte, Ps) ; member(mismo, Ps) ; member(funcion, Ps) ),
    extraer_agente(Ps, Agente), !,
    findall(Otro, mismo_rol(Agente, Otro), Lista),
    rol(Agente, Rol),
    format('Bot: ~w es ~w. Comparten su rol: ~w.~n', [Agente, Rol, Lista]).

% ¿Cuánto cuesta X arma?
responder(Ps) :-
    ( member(cuesta, Ps) ; member(precio, Ps) ; member(costo, Ps) ; member(vale, Ps) ),
    extraer_arma(Ps, Arma), !,
    costo(Arma, Costo),
    format('Bot: El arma ~w cuesta ~w creditos.~n', [Arma, Costo]).

% ¿Cuánto cuestan las habilidades de un agente?
responder(Ps) :-
    ( member(habilidades, Ps) ; member(kit, Ps) ; member(utilidad, Ps) ),
    extraer_agente(Ps, Agente), !,
    costo_kit(Agente, Costo),
    format('Bot: El kit completo de habilidades de ~w cuesta ~w creditos.~n', [Agente, Costo]).

% ¿Qué tipo de ronda corresponde a X créditos?
responder(Ps) :-
    ( member(ronda, Ps) ; member(buy, Ps) ),
    extraer_numero(Ps, Creds), !,
    (   creditos_validos(Creds)
    ->  tipo_ronda(Creds, Tipo),
        format('Bot: Con ~w creditos corresponde una ronda: ~w.~n', [Creds, Tipo])
    ;   writeln('Bot: En Valorant el saldo debe estar entre 0 y 9000 creditos.')
    ).

% ¿Qué compro con X créditos jugando con Y?
responder(Ps) :-
    ( member(compro, Ps) ; member(comprar, Ps) ; member(plan, Ps) ; member(recomiendas, Ps) ),
    extraer_numero(Ps, Creds),
    extraer_agente(Ps, Agente), !,
    (   creditos_validos(Creds)
    ->  extraer_distancia(Ps, Dist),
        recomendar_plan(Creds, Agente, Dist, Tipo, Arma, Hab, Escudo, Resto),
        writeln('Bot: --- PLAN RECOMENDADO ---'),
        format('  - Agente          : ~w~n', [Agente]),
        format('  - Tipo de ronda   : ~w~n', [Tipo]),
        format('  - Arma sugerida   : ~w~n', [Arma]),
        format('  - Gasto utilidad  : ~w creditos~n', [Hab]),
        format('  - Blindaje        : ~w~n', [Escudo]),
        format('  - Saldo restante  : ~w creditos~n', [Resto])
    ;   writeln('Bot: En Valorant el saldo debe estar entre 0 y 9000 creditos.')
    ).

% Caso por defecto (siempre al final de responder/1)
responder(_) :-
    writeln('Bot: No entendi la consulta. Intenta incluir el agente, el arma o tus creditos.').

mostrar_ayuda :-
    writeln('Bot: Ejemplos de frases validas:'),
    writeln('  - "que tipo de arma es la vandal".'),
    writeln('  - "tengo 3900 creditos y estoy jugando sage que me compro".'),
    writeln('  - "cual es el rol de jett y quienes lo comparten".'),
    writeln('  - "cuanto cuesta la operator".'),
    writeln('  - "cuanto cuesta el kit de habilidades de omen".'),
    writeln('  - "salir".').

% -----------------------------------------------------------------------------
% 5. BUCLE CONVERSACIONAL (iniciar/0)
% -----------------------------------------------------------------------------
iniciar :-
    writeln('=================================================='),
    writeln('      CHATBOT ASESOR DE VALORANT INTERACTIVO      '),
    writeln('=================================================='),
    writeln('Bot: Escribe tu frase entre comillas dobles y con punto al final.'),
    writeln('Ejemplo: "tengo 3900 creditos jugando sage que compro".'),
    bucle.

bucle :-
    nl, write('Tu: '),
    read(Entrada),
    (   (Entrada == "salir" ; Entrada == salir ; Entrada == end_of_file)
    ->  writeln('Bot: Chao! Buena suerte en tus partidas.')
    ;   (   string(Entrada)
        ->  tokenizar(Entrada, Palabras),
            responder(Palabras)
        ;   writeln('Bot: Recuerda ingresar la frase entre comillas dobles, ej: "tu pregunta".')
        ),
        bucle
    ).