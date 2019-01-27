create database umls;

use umls;

DROP TABLE IF EXISTS MRSTY;
CREATE TABLE MRSTY (
    CUI	char(8) NOT NULL,
    TUI	char(4) NOT NULL,
    STN	varchar(100) NOT NULL,
    STY	varchar(50) NOT NULL,
    ATUI	varchar(11) NOT NULL,
    CVF	int unsigned
) CHARACTER SET utf8;

-- change the file path below

load data local infile 'C:/xampp/htdocs/umls/META/MRSTY.RRF' into table MRSTY fields terminated by '|' ESCAPED BY '' lines terminated by '\r\n'
(@cui,@tui,@stn,@sty,@atui,@cvf)
SET CUI = @cui,
TUI = @tui,
STN = @stn,
STY = @sty,
ATUI = @atui,
CVF = NULLIF(@cvf,'');

CREATE INDEX X_MRSTY_CUI ON MRSTY(CUI);

ALTER TABLE MRSTY ADD CONSTRAINT X_MRSTY_PK  PRIMARY KEY BTREE (ATUI);

CREATE INDEX X_MRSTY_STY ON MRSTY(STY);

DROP TABLE IF EXISTS MRCONSO;
CREATE TABLE MRCONSO (
    CUI	char(8) NOT NULL,
    LAT	char(3) NOT NULL,
    TS	char(1) NOT NULL,
    LUI	varchar(10) NOT NULL,
    STT	varchar(3) NOT NULL,
    SUI	varchar(10) NOT NULL,
    ISPREF	char(1) NOT NULL,
    AUI	varchar(9) NOT NULL,
    SAUI	varchar(50),
    SCUI	varchar(100),
    SDUI	varchar(100),
    SAB	varchar(40) NOT NULL,
    TTY	varchar(40) NOT NULL,
    CODE	varchar(100) NOT NULL,
    STR	text NOT NULL,
    SRL	int unsigned NOT NULL,
    SUPPRESS	char(1) NOT NULL,
    CVF	int unsigned
) CHARACTER SET utf8;

-- change the file path below

load data local infile 'C:/xampp/htdocs/umls/META/MRCONSO.RRF' into table MRCONSO fields terminated by '|' ESCAPED BY '' lines terminated by '\r\n'
(@cui,@lat,@ts,@lui,@stt,@sui,@ispref,@aui,@saui,@scui,@sdui,@sab,@tty,@code,@str,@srl,@suppress,@cvf)
SET CUI = @cui,
LAT = @lat,
TS = @ts,
LUI = @lui,
STT = @stt,
SUI = @sui,
ISPREF = @ispref,
AUI = @aui,
SAUI = NULLIF(@saui,''),
SCUI = NULLIF(@scui,''),
SDUI = NULLIF(@sdui,''),
SAB = @sab,
TTY = @tty,
CODE = @code,
STR = @str,
SRL = @srl,
SUPPRESS = @suppress,
CVF = NULLIF(@cvf,'');


CREATE INDEX X_MRCONSO_CUI ON MRCONSO(CUI);

ALTER TABLE MRCONSO ADD CONSTRAINT X_MRCONSO_PK  PRIMARY KEY BTREE (AUI);

CREATE INDEX X_MRCONSO_SUI ON MRCONSO(SUI);

CREATE INDEX X_MRCONSO_LUI ON MRCONSO(LUI);

CREATE INDEX X_MRCONSO_CODE ON MRCONSO(CODE);

CREATE INDEX X_MRCONSO_SAB_TTY ON MRCONSO(SAB,TTY);

CREATE INDEX X_MRCONSO_SCUI ON MRCONSO(SCUI);

CREATE INDEX X_MRCONSO_SDUI ON MRCONSO(SDUI);

CREATE INDEX X_MRCONSO_STR ON MRCONSO(STR(255));