# PID `CERTI_E331A` 최신버전(v13) vs 이전버전(v12) 비교 분석 보고서

## 1. 개요 및 변경 요약
- **대상 PID**: `CERTI_E331A` (E331A 부품인증/인증번호 로직)
- **이전 버전 (`VERSION = 12`)**: 총 **61 행** (등록일: 2025-12-04, 사번: 2033224)
- **최신 버전 (`VERSION = 13`)**: 총 **67 행** (등록일: 2026-08-13, 사번: 2033224, **+6행 신규 추가**)
- **주요 변경 사항 핵심 요약**:
  1. **신규 행 추가 (+6행)**: **NO 62, 63, 64, 65, 66, 67** 6개 행 신규 등록 (C-DOOR2 부품인증 검증/체크 로직 보완)
  2. **C-DOOR2 인증 사양 세분화 및 신규 인증번호 반영 (NO 51 ~ 58)**: 기존의 단순 체크 로직이 `AAA13-J001-24007`, `AAA13-J001-24008`, `AAA13-J001-25001`, `AAA13-J001-26011` ~ `26014` 등 신규 인증번호 매핑 로직으로 대폭 개편됨
  3. **체크 라벨 흐름 변경 (GOTO CHK2)**: NO 51~58 행의 `GOTO`를 `CHK2`로 지정하여 부품인증 범위 검증 구간(`CHK2`)으로 흐름 연결

## 2. 세부 변경 사항 정밀 분석

### 2.1 신규 추가된 행 (+6건: NO 62 ~ 67)
최신 버전(v13)에서 C-DOOR2 부품인증 검증(인증번호 유무, JJ/HH 범위 이탈 체크)을 완성하기 위해 추가된 6개 행입니다.

| 신규 행 번호 (NO) | ADDR / GOTO | 주요 조건 (SPEC / CON) | 산출 결과 (KEY / VAL) | 비고 |
|---|---|---|---|---|
| **NO 62** | `-` / `-` | `C_DOOR_CERTI_NO_2`: `N`<br>`EL_DPW`: `,N,G`<br>`EL_BCDGD`: `G` | `CHK`: `- C-DOOR2 부품인증(350J) 없음`<br>`CERTI_CMT_E331A`: `{CERTI_CMT_E331A}{CHK}` | 신규 로직 추가 |
| **NO 63** | `-` / `-` | `C_DOOR_CERTI_NO_2`: `N`<br>`EL_DPW`: `,1,2` | `CHK`: `- C-DOOR2 부품인증(350J) 없음`<br>`CERTI_CMT_E331A`: `{CERTI_CMT_E331A}{CHK}` | 신규 로직 추가 |
| **NO 64** | `-` / `-` | `C_DOOR_CERTI_NO_2`: `!N`<br>`EL_ECJJ`: `<{JJ_MIN}` | `CHK`: `- C-DOOR2 부품인증(350J) JJ 범위 벗어남(현장사양:{EL_ECJJ}mm, 인증범위:{JJ_MIN}~{JJ_MAX}mm) (부품인증번호 : {C_DOOR_CERTI_NO_2_VER})`<br>`CERTI_CMT_E331A`: `{CERTI_CMT_E331A}{CHK}` | 신규 로직 추가 |
| **NO 65** | `-` / `-` | `C_DOOR_CERTI_NO_2`: `!N`<br>`EL_ECJJ`: `>{JJ_MAX}` | `CHK`: `- C-DOOR2 부품인증(350J) JJ 범위 벗어남(현장사양:{EL_ECJJ}mm, 인증범위:{JJ_MIN}~{JJ_MAX}mm) (부품인증번호 : {C_DOOR_CERTI_NO_2_VER})`<br>`CERTI_CMT_E331A`: `{CERTI_CMT_E331A}{CHK}` | 신규 로직 추가 |
| **NO 66** | `-` / `-` | `C_DOOR_CERTI_NO_2`: `!N`<br>`EL_ECHH`: `<{HH_MIN}` | `CHK`: `- C-DOOR2 부품인증(350J) HH 범위 벗어남(현장사양:{EL_ECHH}mm, 인증범위:{HH_MIN}~{HH_MAX}mm) (부품인증번호 : {C_DOOR_CERTI_NO_2_VER})`<br>`CERTI_CMT_E331A`: `{CERTI_CMT_E331A}{CHK}` | 신규 로직 추가 |
| **NO 67** | `-` / `-` | `C_DOOR_CERTI_NO_2`: `!N`<br>`EL_ECHH`: `>{HH_MAX}` | `CHK`: `- C-DOOR2 부품인증(350J) HH 범위 벗어남(현장사양:{EL_ECHH}mm, 인증범위:{HH_MIN}~{HH_MAX}mm) (부품인증번호 : {C_DOOR_CERTI_NO_2_VER})`<br>`CERTI_CMT_E331A`: `{CERTI_CMT_E331A}{CHK}` | 신규 로직 추가 |

### 2.2 기존 행 수정 사항 (총 12건: NO 50 ~ 61)
기존 v12 버전의 NO 51~61 행이 v13에서 C-DOOR2 부품인증 매핑 테이블 로직으로 개편되었습니다.

#### ■ NO 24 행 변경 내역
- **GOTO**: `-` → `CHK`
- **SPEC1/CON1**: (`-`, `-`) → (`EL_ACD2`, `?KS?`)
- **SPEC2/CON2**: (`-`, `-`) → (`EL_AOPEN`, `1SCO`)
- **SPEC3/CON3**: (`-`, `-`) → (`EL_ECDOP`, `P2H`)
- **SPEC4/CON4**: (`-`, `-`) → (`TYPE_450J`, `GLASTL`)
- **SPEC5/CON5**: (`-`, `-`) → (`EL_DPW`, `N`)
- **SPEC6/CON6**: (`-`, `-`) → (`EL_ECJJ`, `>=900,<=1100`)
- **SPEC7/CON7**: (`-`, `-`) → (`EL_ECHH`, `>=2000,<=2400`)
- **SPEC8/CON8**: (`-`, `-`) → (`EL_BCDGD`, `N`)
- **SPEC9/CON9**: (`-`, `-`) → (`EL_BCDAD`, `,N,A`)
- **SPEC10/CON10**: (`-`, `-`) → (`EL_BCS`, `AL`)
- **KEY1/VAL1**: (`-`, `-`) → (`C_DOOR_CERTI_NO`, `AAA13-J001-26011`)
- **KEY2/VAL2**: (`-`, `-`) → (`C_DOOR_CERTI_NO_VER`, `AAA13-J001-26011`)
- **KEY3/VAL3**: (`-`, `-`) → (`JJ_MIN`, `900`)
- **KEY4/VAL4**: (`-`, `-`) → (`JJ_MAX`, `1100`)
- **KEY5/VAL5**: (`-`, `-`) → (`HH_MIN`, `2000`)
- **KEY6/VAL6**: (`-`, `-`) → (`HH_MAX`, `2400`)

#### ■ NO 25 행 변경 내역
- **ADDR**: `CHK` → `-`
- **GOTO**: `-` → `CHK`
- **SPEC1/CON1**: (`-`, `-`) → (`EL_ACD2`, `?KS?`)
- **SPEC2/CON2**: (`-`, `-`) → (`EL_AOPEN`, `1SCO`)
- **SPEC3/CON3**: (`-`, `-`) → (`EL_ECDOP`, `P2H`)
- **SPEC4/CON4**: (`-`, `-`) → (`TYPE_450J`, `GLASTL`)
- **SPEC5/CON5**: (`-`, `-`) → (`EL_DPW`, `N`)
- **SPEC6/CON6**: (`-`, `-`) → (`EL_ECJJ`, `>=900,<=1100`)
- **SPEC7/CON7**: (`-`, `-`) → (`EL_ECHH`, `>=2000,<=2400`)
- **SPEC8/CON8**: (`-`, `-`) → (`EL_BCDGD`, `N`)
- **SPEC9/CON9**: (`-`, `-`) → (`EL_BCDAD`, `,D,AD`)
- **SPEC10/CON10**: (`-`, `-`) → (`EL_BCS`, `AL`)
- **KEY1/VAL1**: (`-`, `-`) → (`C_DOOR_CERTI_NO`, `AAA13-J001-26012`)
- **KEY2/VAL2**: (`-`, `-`) → (`C_DOOR_CERTI_NO_VER`, `AAA13-J001-26012C`)
- **KEY3/VAL3**: (`-`, `-`) → (`JJ_MIN`, `900`)
- **KEY4/VAL4**: (`-`, `-`) → (`JJ_MAX`, `1100`)
- **KEY5/VAL5**: (`-`, `-`) → (`HH_MIN`, `2000`)
- **KEY6/VAL6**: (`-`, `-`) → (`HH_MAX`, `2400`)

#### ■ NO 26 행 변경 내역
- **GOTO**: `-` → `CHK`
- **SPEC1/CON1**: (`-`, `-`) → (`EL_ACD2`, `?KS?`)
- **SPEC2/CON2**: (`-`, `-`) → (`EL_AOPEN`, `1SCO`)
- **SPEC3/CON3**: (`-`, `-`) → (`EL_ECDOP`, `P2H`)
- **SPEC4/CON4**: (`-`, `-`) → (`TYPE_450J`, `GLASTL`)
- **SPEC5/CON5**: (`-`, `-`) → (`EL_DPW`, `N`)
- **SPEC6/CON6**: (`-`, `-`) → (`EL_ECJJ`, `>=1200,<=1500`)
- **SPEC7/CON7**: (`-`, `-`) → (`EL_ECHH`, `>=2000,<=2400`)
- **SPEC8/CON8**: (`-`, `-`) → (`EL_BCDGD`, `N`)
- **SPEC9/CON9**: (`-`, `-`) → (`EL_BCDAD`, `,N,A`)
- **SPEC10/CON10**: (`-`, `-`) → (`EL_BCS`, `AL`)
- **KEY1/VAL1**: (`CHK`, `-`) → (`C_DOOR_CERTI_NO`, `AAA13-J001-26013`)
- **KEY2/VAL2**: (`CERTI_CMT_E331A`, `-`) → (`C_DOOR_CERTI_NO_VER`, `AAA13-J001-26013`)
- **KEY3/VAL3**: (`-`, `-`) → (`JJ_MIN`, `1200`)
- **KEY4/VAL4**: (`-`, `-`) → (`JJ_MAX`, `1500`)
- **KEY5/VAL5**: (`-`, `-`) → (`HH_MIN`, `2000`)
- **KEY6/VAL6**: (`-`, `-`) → (`HH_MAX`, `2400`)

#### ■ NO 27 행 변경 내역
- **GOTO**: `-` → `CHK`
- **SPEC1/CON1**: (`C_DOOR_CERTI_NO`, `N`) → (`EL_ACD2`, `?KS?`)
- **SPEC2/CON2**: (`TYPE_450J`, `?GLASTL?`) → (`EL_AOPEN`, `1SCO`)
- **SPEC3/CON3**: (`-`, `-`) → (`EL_ECDOP`, `P2H`)
- **SPEC4/CON4**: (`-`, `-`) → (`TYPE_450J`, `GLASTL`)
- **SPEC5/CON5**: (`-`, `-`) → (`EL_DPW`, `N`)
- **SPEC6/CON6**: (`-`, `-`) → (`EL_ECJJ`, `>=1200,<=1500`)
- **SPEC7/CON7**: (`-`, `-`) → (`EL_ECHH`, `>=2000,<=2400`)
- **SPEC8/CON8**: (`-`, `-`) → (`EL_BCDGD`, `N`)
- **SPEC9/CON9**: (`-`, `-`) → (`EL_BCDAD`, `,D,AD`)
- **SPEC10/CON10**: (`-`, `-`) → (`EL_BCS`, `AL`)
- **KEY1/VAL1**: (`CHK`, `- C-DOOR 부품인증(350J) 없음`) → (`C_DOOR_CERTI_NO`, `AAA13-J001-26014`)
- **KEY2/VAL2**: (`CERTI_CMT_E331A`, `{CERTI_CMT_E331A}{CHK}`) → (`C_DOOR_CERTI_NO_VER`, `AAA13-J001-26014C`)
- **KEY3/VAL3**: (`-`, `-`) → (`JJ_MIN`, `1200`)
- **KEY4/VAL4**: (`-`, `-`) → (`JJ_MAX`, `1500`)
- **KEY5/VAL5**: (`-`, `-`) → (`HH_MIN`, `2000`)
- **KEY6/VAL6**: (`-`, `-`) → (`HH_MAX`, `2400`)

#### ■ NO 28 행 변경 내역
- **ADDR**: `-` → `CHK`
- **SPEC1/CON1**: (`C_DOOR_CERTI_NO`, `N`) → (`-`, `-`)
- **SPEC2/CON2**: (`EL_DPW`, `,N,G`) → (`-`, `-`)
- **SPEC3/CON3**: (`EL_BCDGD`, `G`) → (`-`, `-`)
- **KEY1/VAL1**: (`CHK`, `- C-DOOR 부품인증(350J) 없음`) → (`-`, `-`)
- **KEY2/VAL2**: (`CERTI_CMT_E331A`, `{CERTI_CMT_E331A}{CHK}`) → (`-`, `-`)

#### ■ NO 29 행 변경 내역
- **SPEC1/CON1**: (`C_DOOR_CERTI_NO`, `N`) → (`-`, `-`)
- **SPEC2/CON2**: (`EL_DPW`, `,1,2`) → (`-`, `-`)
- **KEY1/VAL1**: (`CHK`, `- C-DOOR 부품인증(350J) 없음`) → (`CHK`, `-`)
- **KEY2/VAL2**: (`CERTI_CMT_E331A`, `{CERTI_CMT_E331A}{CHK}`) → (`CERTI_CMT_E331A`, `-`)

#### ■ NO 30 행 변경 내역
- **SPEC1/CON1**: (`C_DOOR_CERTI_NO`, `!N`) → (`C_DOOR_CERTI_NO`, `N`)
- **SPEC2/CON2**: (`EL_ECJJ`, `<{JJ_MIN}`) → (`TYPE_450J`, `?GLASTL?`)
- **KEY1/VAL1**: (`CHK`, `- C-DOOR 부품인증(350J) JJ 범위 벗어남(현장사양:{EL_ECJJ}mm, 인증범위:{JJ_MIN}~{JJ_MAX}mm) (부품인증번호 : {C_DOOR_CERTI_NO_VER})`) → (`CHK`, `- C-DOOR 부품인증(350J) 없음`)

#### ■ NO 31 행 변경 내역
- **SPEC1/CON1**: (`C_DOOR_CERTI_NO`, `!N`) → (`C_DOOR_CERTI_NO`, `N`)
- **SPEC2/CON2**: (`EL_ECJJ`, `>{JJ_MAX}`) → (`EL_DPW`, `,N,G`)
- **SPEC3/CON3**: (`-`, `-`) → (`EL_BCDGD`, `G`)
- **KEY1/VAL1**: (`CHK`, `- C-DOOR 부품인증(350J) JJ 범위 벗어남(현장사양:{EL_ECJJ}mm, 인증범위:{JJ_MIN}~{JJ_MAX}mm) (부품인증번호 : {C_DOOR_CERTI_NO_VER})`) → (`CHK`, `- C-DOOR 부품인증(350J) 없음`)

#### ■ NO 32 행 변경 내역
- **SPEC1/CON1**: (`C_DOOR_CERTI_NO`, `!N`) → (`C_DOOR_CERTI_NO`, `N`)
- **SPEC2/CON2**: (`EL_ECHH`, `<{HH_MIN}`) → (`EL_DPW`, `,1,2`)
- **KEY1/VAL1**: (`CHK`, `- C-DOOR 부품인증(350J) HH 범위 벗어남(현장사양:{EL_ECHH}mm, 인증범위:{HH_MIN}~{HH_MAX}mm) (부품인증번호 : {C_DOOR_CERTI_NO_VER})`) → (`CHK`, `- C-DOOR 부품인증(350J) 없음`)

#### ■ NO 33 행 변경 내역
- **SPEC2/CON2**: (`EL_ECHH`, `>{HH_MAX}`) → (`EL_ECJJ`, `<{JJ_MIN}`)
- **KEY1/VAL1**: (`CHK`, `- C-DOOR 부품인증(350J) HH 범위 벗어남(현장사양:{EL_ECHH}mm, 인증범위:{HH_MIN}~{HH_MAX}mm) (부품인증번호 : {C_DOOR_CERTI_NO_VER})`) → (`CHK`, `- C-DOOR 부품인증(350J) JJ 범위 벗어남(현장사양:{EL_ECJJ}mm, 인증범위:{JJ_MIN}~{JJ_MAX}mm) (부품인증번호 : {C_DOOR_CERTI_NO_VER})`)

#### ■ NO 34 행 변경 내역
- **SPEC1/CON1**: (`-`, `-`) → (`C_DOOR_CERTI_NO`, `!N`)
- **SPEC2/CON2**: (`-`, `-`) → (`EL_ECJJ`, `>{JJ_MAX}`)
- **KEY1/VAL1**: (`-`, `-`) → (`CHK`, `- C-DOOR 부품인증(350J) JJ 범위 벗어남(현장사양:{EL_ECJJ}mm, 인증범위:{JJ_MIN}~{JJ_MAX}mm) (부품인증번호 : {C_DOOR_CERTI_NO_VER})`)
- **KEY2/VAL2**: (`-`, `-`) → (`CERTI_CMT_E331A`, `{CERTI_CMT_E331A}{CHK}`)

#### ■ NO 35 행 변경 내역
- **SPEC1/CON1**: (`-`, `-`) → (`C_DOOR_CERTI_NO`, `!N`)
- **SPEC2/CON2**: (`-`, `-`) → (`EL_ECHH`, `<{HH_MIN}`)
- **KEY1/VAL1**: (`-`, `-`) → (`CHK`, `- C-DOOR 부품인증(350J) HH 범위 벗어남(현장사양:{EL_ECHH}mm, 인증범위:{HH_MIN}~{HH_MAX}mm) (부품인증번호 : {C_DOOR_CERTI_NO_VER})`)
- **KEY2/VAL2**: (`-`, `-`) → (`CERTI_CMT_E331A`, `{CERTI_CMT_E331A}{CHK}`)

#### ■ NO 36 행 변경 내역
- **ADDR**: `MAIN2` → `-`
- **SPEC1/CON1**: (`-`, `-`) → (`C_DOOR_CERTI_NO`, `!N`)
- **SPEC2/CON2**: (`-`, `-`) → (`EL_ECHH`, `>{HH_MAX}`)
- **KEY1/VAL1**: (`-`, `-`) → (`CHK`, `- C-DOOR 부품인증(350J) HH 범위 벗어남(현장사양:{EL_ECHH}mm, 인증범위:{HH_MIN}~{HH_MAX}mm) (부품인증번호 : {C_DOOR_CERTI_NO_VER})`)
- **KEY2/VAL2**: (`-`, `-`) → (`CERTI_CMT_E331A`, `{CERTI_CMT_E331A}{CHK}`)

#### ■ NO 37 행 변경 내역
- **GOTO**: `STOP` → `-`
- **SPEC1/CON1**: (`EL_BCDM2`, `N`) → (`-`, `-`)

#### ■ NO 38 행 변경 내역
- **KEY1/VAL1**: (`C_DOOR_CERTI_NO_2`, `-`) → (`-`, `-`)
- **KEY2/VAL2**: (`C_DOOR_CERTI_NO_2_VER`, `-`) → (`-`, `-`)
- **KEY3/VAL3**: (`JJ_MIN`, `-`) → (`-`, `-`)
- **KEY4/VAL4**: (`JJ_MAX`, `-`) → (`-`, `-`)
- **KEY5/VAL5**: (`HH_MIN`, `-`) → (`-`, `-`)
- **KEY6/VAL6**: (`HH_MAX`, `-`) → (`-`, `-`)

#### ■ NO 39 행 변경 내역
- **ADDR**: `-` → `MAIN2`
- **KEY1/VAL1**: (`VAR_MATERIAL`, `{EL_BCDM2}`) → (`-`, `-`)
- **KEY2/VAL2**: (`CALL`, `CALC_MATERIAL_CODE`) → (`-`, `-`)

#### ■ NO 40 행 변경 내역
- **GOTO**: `CHK2` → `STOP`
- **SPEC1/CON1**: (`EL_ACD2`, `?KS?`) → (`EL_BCDM2`, `N`)
- **SPEC2/CON2**: (`EL_AOPEN`, `1SCO`) → (`-`, `-`)
- **SPEC3/CON3**: (`EL_ECDOP`, `,P2,P2S`) → (`-`, `-`)
- **SPEC4/CON4**: (`TYPE_450J`, `GLASTL`) → (`-`, `-`)
- **SPEC5/CON5**: (`EL_DPW`, `N`) → (`-`, `-`)
- **SPEC6/CON6**: (`EL_ECJJ`, `>=700,<=1100`) → (`-`, `-`)
- **SPEC7/CON7**: (`EL_ECHH`, `>=2000,<=2400`) → (`-`, `-`)
- **SPEC8/CON8**: (`EL_BCDGD`, `N`) → (`-`, `-`)
- **SPEC9/CON9**: (`EL_BCDAD`, `,N,A`) → (`-`, `-`)
- **SPEC10/CON10**: (`EL_BCS`, `,AL,GL`) → (`-`, `-`)
- **KEY1/VAL1**: (`C_DOOR_CERTI_NO_2`, `AAA13-J001-19001`) → (`-`, `-`)
- **KEY2/VAL2**: (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-19001D`) → (`-`, `-`)
- **KEY3/VAL3**: (`JJ_MIN`, `700`) → (`-`, `-`)
- **KEY4/VAL4**: (`JJ_MAX`, `1100`) → (`-`, `-`)
- **KEY5/VAL5**: (`HH_MIN`, `2000`) → (`-`, `-`)
- **KEY6/VAL6**: (`HH_MAX`, `2400`) → (`-`, `-`)

#### ■ NO 41 행 변경 내역
- **GOTO**: `CHK2` → `-`
- **SPEC1/CON1**: (`EL_ACD2`, `?KS?`) → (`-`, `-`)
- **SPEC2/CON2**: (`EL_AOPEN`, `1SCO`) → (`-`, `-`)
- **SPEC3/CON3**: (`EL_ECDOP`, `,P2,P2S`) → (`-`, `-`)
- **SPEC4/CON4**: (`TYPE_450J`, `SPCC_T1.2`) → (`-`, `-`)
- **SPEC5/CON5**: (`EL_DPW`, `,1,2`) → (`-`, `-`)
- **SPEC6/CON6**: (`EL_ECJJ`, `800`) → (`-`, `-`)
- **SPEC7/CON7**: (`EL_ECHH`, `2100`) → (`-`, `-`)
- **SPEC8/CON8**: (`EL_BCDGD`, `N`) → (`-`, `-`)
- **KEY1/VAL1**: (`C_DOOR_CERTI_NO_2`, `AAA13-J001-19014`) → (`C_DOOR_CERTI_NO_2`, `-`)
- **KEY2/VAL2**: (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-19014B`) → (`C_DOOR_CERTI_NO_2_VER`, `-`)
- **KEY3/VAL3**: (`JJ_MIN`, `800`) → (`JJ_MIN`, `-`)
- **KEY4/VAL4**: (`JJ_MAX`, `800`) → (`JJ_MAX`, `-`)
- **KEY5/VAL5**: (`HH_MIN`, `2100`) → (`HH_MIN`, `-`)
- **KEY6/VAL6**: (`HH_MAX`, `2100`) → (`HH_MAX`, `-`)

#### ■ NO 42 행 변경 내역
- **GOTO**: `CHK2` → `-`
- **SPEC1/CON1**: (`EL_ACD2`, `?KS?`) → (`-`, `-`)
- **SPEC2/CON2**: (`EL_AOPEN`, `1SCO`) → (`-`, `-`)
- **SPEC3/CON3**: (`EL_ECDOP`, `,P2,P2S`) → (`-`, `-`)
- **SPEC4/CON4**: (`TYPE_450J`, `SPCC_T1.2`) → (`-`, `-`)
- **SPEC5/CON5**: (`EL_DPW`, `,1,2`) → (`-`, `-`)
- **SPEC6/CON6**: (`EL_ECJJ`, `900`) → (`-`, `-`)
- **SPEC7/CON7**: (`EL_ECHH`, `2100`) → (`-`, `-`)
- **SPEC8/CON8**: (`EL_BCDGD`, `N`) → (`-`, `-`)
- **KEY1/VAL1**: (`C_DOOR_CERTI_NO_2`, `AAA13-J001-19015`) → (`VAR_MATERIAL`, `{EL_BCDM2}`)
- **KEY2/VAL2**: (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-19015B`) → (`CALL`, `CALC_MATERIAL_CODE`)
- **KEY3/VAL3**: (`JJ_MIN`, `900`) → (`-`, `-`)
- **KEY4/VAL4**: (`JJ_MAX`, `900`) → (`-`, `-`)
- **KEY5/VAL5**: (`HH_MIN`, `2100`) → (`-`, `-`)
- **KEY6/VAL6**: (`HH_MAX`, `2100`) → (`-`, `-`)

#### ■ NO 43 행 변경 내역
- **SPEC4/CON4**: (`TYPE_450J`, `-`) → (`TYPE_450J`, `GLASTL`)
- **SPEC5/CON5**: (`EL_DPW`, `,N,G`) → (`EL_DPW`, `N`)
- **SPEC6/CON6**: (`EL_ECJJ`, `>=700,<=1200`) → (`EL_ECJJ`, `>=700,<=1100`)
- **SPEC8/CON8**: (`EL_BCDGD`, `G`) → (`EL_BCDGD`, `N`)
- **SPEC10/CON10**: (`EL_BCS`, `AL`) → (`EL_BCS`, `,AL,GL`)
- **KEY1/VAL1**: (`C_DOOR_CERTI_NO_2`, `AAA13-J001-20002`) → (`C_DOOR_CERTI_NO_2`, `AAA13-J001-19001`)
- **KEY2/VAL2**: (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-20002B`) → (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-19001D`)
- **KEY4/VAL4**: (`JJ_MAX`, `1200`) → (`JJ_MAX`, `1100`)

#### ■ NO 44 행 변경 내역
- **SPEC4/CON4**: (`TYPE_450J`, `SUS_T1.2`) → (`TYPE_450J`, `SPCC_T1.2`)
- **KEY1/VAL1**: (`C_DOOR_CERTI_NO_2`, `AAA13-J001-20003`) → (`C_DOOR_CERTI_NO_2`, `AAA13-J001-19014`)
- **KEY2/VAL2**: (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-20003A`) → (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-19014B`)

#### ■ NO 45 행 변경 내역
- **SPEC4/CON4**: (`TYPE_450J`, `SUS_T1.2`) → (`TYPE_450J`, `SPCC_T1.2`)
- **KEY1/VAL1**: (`C_DOOR_CERTI_NO_2`, `AAA13-J001-20004`) → (`C_DOOR_CERTI_NO_2`, `AAA13-J001-19015`)
- **KEY2/VAL2**: (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-20004A`) → (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-19015B`)

#### ■ NO 46 행 변경 내역
- **SPEC4/CON4**: (`TYPE_450J`, `GLASTL`) → (`TYPE_450J`, `-`)
- **SPEC5/CON5**: (`EL_DPW`, `N`) → (`EL_DPW`, `,N,G`)
- **SPEC6/CON6**: (`EL_ECJJ`, `>=800,<=1100`) → (`EL_ECJJ`, `>=700,<=1200`)
- **SPEC8/CON8**: (`EL_BCDGD`, `N`) → (`EL_BCDGD`, `G`)
- **SPEC9/CON9**: (`EL_BCDAD`, `,D,AD`) → (`EL_BCDAD`, `,N,A`)
- **KEY1/VAL1**: (`C_DOOR_CERTI_NO_2`, `AAA13-J001-25004`) → (`C_DOOR_CERTI_NO_2`, `AAA13-J001-20002`)
- **KEY2/VAL2**: (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-25004`) → (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-20002B`)
- **KEY3/VAL3**: (`JJ_MIN`, `800`) → (`JJ_MIN`, `700`)
- **KEY4/VAL4**: (`JJ_MAX`, `1100`) → (`JJ_MAX`, `1200`)

#### ■ NO 47 행 변경 내역
- **SPEC4/CON4**: (`TYPE_450J`, `GLASTL`) → (`TYPE_450J`, `SUS_T1.2`)
- **SPEC5/CON5**: (`EL_DPW`, `N`) → (`EL_DPW`, `,1,2`)
- **SPEC6/CON6**: (`EL_ECJJ`, `1200`) → (`EL_ECJJ`, `800`)
- **SPEC7/CON7**: (`EL_ECHH`, `>=2000,<=2400`) → (`EL_ECHH`, `2100`)
- **SPEC9/CON9**: (`EL_BCDAD`, `,D,AD`) → (`-`, `-`)
- **SPEC10/CON10**: (`EL_BCS`, `AL`) → (`-`, `-`)
- **KEY1/VAL1**: (`C_DOOR_CERTI_NO_2`, `AAA13-J001-25006`) → (`C_DOOR_CERTI_NO_2`, `AAA13-J001-20003`)
- **KEY2/VAL2**: (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-25006`) → (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-20003A`)
- **KEY3/VAL3**: (`JJ_MIN`, `1200`) → (`JJ_MIN`, `800`)
- **KEY4/VAL4**: (`JJ_MAX`, `1200`) → (`JJ_MAX`, `800`)
- **KEY5/VAL5**: (`HH_MIN`, `2000`) → (`HH_MIN`, `2100`)
- **KEY6/VAL6**: (`HH_MAX`, `2400`) → (`HH_MAX`, `2100`)

#### ■ NO 48 행 변경 내역
- **SPEC3/CON3**: (`EL_ECDOP`, `MH1`) → (`EL_ECDOP`, `,P2,P2S`)
- **SPEC4/CON4**: (`TYPE_450J`, `GLASTL`) → (`TYPE_450J`, `SUS_T1.2`)
- **SPEC5/CON5**: (`EL_DPW`, `N`) → (`EL_DPW`, `,1,2`)
- **SPEC6/CON6**: (`EL_ECJJ`, `>=800,<=1100`) → (`EL_ECJJ`, `900`)
- **SPEC7/CON7**: (`EL_ECHH`, `>=2000,<=2400`) → (`EL_ECHH`, `2100`)
- **SPEC9/CON9**: (`EL_BCDAD`, `,N,A`) → (`-`, `-`)
- **SPEC10/CON10**: (`EL_BCS`, `AL`) → (`-`, `-`)
- **KEY1/VAL1**: (`C_DOOR_CERTI_NO_2`, `AAA13-J001-24003`) → (`C_DOOR_CERTI_NO_2`, `AAA13-J001-20004`)
- **KEY2/VAL2**: (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-24003A`) → (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-20004A`)
- **KEY3/VAL3**: (`JJ_MIN`, `800`) → (`JJ_MIN`, `900`)
- **KEY4/VAL4**: (`JJ_MAX`, `1100`) → (`JJ_MAX`, `900`)
- **KEY5/VAL5**: (`HH_MIN`, `2000`) → (`HH_MIN`, `2100`)
- **KEY6/VAL6**: (`HH_MAX`, `2400`) → (`HH_MAX`, `2100`)

#### ■ NO 49 행 변경 내역
- **SPEC3/CON3**: (`EL_ECDOP`, `MH1`) → (`EL_ECDOP`, `,P2,P2S`)
- **SPEC6/CON6**: (`EL_ECJJ`, `>=1200,<=1500`) → (`EL_ECJJ`, `>=800,<=1100`)
- **SPEC9/CON9**: (`EL_BCDAD`, `,N,A`) → (`EL_BCDAD`, `,D,AD`)
- **KEY1/VAL1**: (`C_DOOR_CERTI_NO_2`, `AAA13-J001-24007`) → (`C_DOOR_CERTI_NO_2`, `AAA13-J001-25004`)
- **KEY2/VAL2**: (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-24007`) → (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-25004`)
- **KEY3/VAL3**: (`JJ_MIN`, `1200`) → (`JJ_MIN`, `800`)
- **KEY4/VAL4**: (`JJ_MAX`, `1500`) → (`JJ_MAX`, `1100`)

#### ■ NO 50 행 변경 내역
- **SPEC3/CON3**: (`EL_ECDOP`, `MH1`) → (`EL_ECDOP`, `,P2,P2S`)
- **SPEC6/CON6**: (`EL_ECJJ`, `>=800,<=1100`) → (`EL_ECJJ`, `1200`)
- **KEY1/VAL1**: (`C_DOOR_CERTI_NO_2`, `AAA13-J001-24008`) → (`C_DOOR_CERTI_NO_2`, `AAA13-J001-25006`)
- **KEY2/VAL2**: (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-24008`) → (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-25006`)
- **KEY3/VAL3**: (`JJ_MIN`, `800`) → (`JJ_MIN`, `1200`)
- **KEY4/VAL4**: (`JJ_MAX`, `1100`) → (`JJ_MAX`, `1200`)

#### ■ NO 51 행 변경 내역
- **SPEC6/CON6**: (`EL_ECJJ`, `>=1200,<=1500`) → (`EL_ECJJ`, `>=800,<=1100`)
- **SPEC9/CON9**: (`EL_BCDAD`, `,D,AD`) → (`EL_BCDAD`, `,N,A`)
- **KEY1/VAL1**: (`C_DOOR_CERTI_NO_2`, `AAA13-J001-25001`) → (`C_DOOR_CERTI_NO_2`, `AAA13-J001-24003`)
- **KEY2/VAL2**: (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-25001`) → (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-24003A`)
- **KEY3/VAL3**: (`JJ_MIN`, `1200`) → (`JJ_MIN`, `800`)
- **KEY4/VAL4**: (`JJ_MAX`, `1500`) → (`JJ_MAX`, `1100`)

#### ■ NO 52 행 변경 내역
- **GOTO**: `-` → `CHK2`
- **SPEC1/CON1**: (`-`, `-`) → (`EL_ACD2`, `?KS?`)
- **SPEC2/CON2**: (`-`, `-`) → (`EL_AOPEN`, `1SCO`)
- **SPEC3/CON3**: (`-`, `-`) → (`EL_ECDOP`, `MH1`)
- **SPEC4/CON4**: (`-`, `-`) → (`TYPE_450J`, `GLASTL`)
- **SPEC5/CON5**: (`-`, `-`) → (`EL_DPW`, `N`)
- **SPEC6/CON6**: (`-`, `-`) → (`EL_ECJJ`, `>=1200,<=1500`)
- **SPEC7/CON7**: (`-`, `-`) → (`EL_ECHH`, `>=2000,<=2400`)
- **SPEC8/CON8**: (`-`, `-`) → (`EL_BCDGD`, `N`)
- **SPEC9/CON9**: (`-`, `-`) → (`EL_BCDAD`, `,N,A`)
- **SPEC10/CON10**: (`-`, `-`) → (`EL_BCS`, `AL`)
- **KEY1/VAL1**: (`-`, `-`) → (`C_DOOR_CERTI_NO_2`, `AAA13-J001-24007`)
- **KEY2/VAL2**: (`-`, `-`) → (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-24007`)
- **KEY3/VAL3**: (`-`, `-`) → (`JJ_MIN`, `1200`)
- **KEY4/VAL4**: (`-`, `-`) → (`JJ_MAX`, `1500`)
- **KEY5/VAL5**: (`-`, `-`) → (`HH_MIN`, `2000`)
- **KEY6/VAL6**: (`-`, `-`) → (`HH_MAX`, `2400`)

#### ■ NO 53 행 변경 내역
- **ADDR**: `CHK2` → `-`
- **GOTO**: `-` → `CHK2`
- **SPEC1/CON1**: (`-`, `-`) → (`EL_ACD2`, `?KS?`)
- **SPEC2/CON2**: (`-`, `-`) → (`EL_AOPEN`, `1SCO`)
- **SPEC3/CON3**: (`-`, `-`) → (`EL_ECDOP`, `MH1`)
- **SPEC4/CON4**: (`-`, `-`) → (`TYPE_450J`, `GLASTL`)
- **SPEC5/CON5**: (`-`, `-`) → (`EL_DPW`, `N`)
- **SPEC6/CON6**: (`-`, `-`) → (`EL_ECJJ`, `>=800,<=1100`)
- **SPEC7/CON7**: (`-`, `-`) → (`EL_ECHH`, `>=2000,<=2400`)
- **SPEC8/CON8**: (`-`, `-`) → (`EL_BCDGD`, `N`)
- **SPEC9/CON9**: (`-`, `-`) → (`EL_BCDAD`, `,D,AD`)
- **SPEC10/CON10**: (`-`, `-`) → (`EL_BCS`, `AL`)
- **KEY1/VAL1**: (`-`, `-`) → (`C_DOOR_CERTI_NO_2`, `AAA13-J001-24008`)
- **KEY2/VAL2**: (`-`, `-`) → (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-24008`)
- **KEY3/VAL3**: (`-`, `-`) → (`JJ_MIN`, `800`)
- **KEY4/VAL4**: (`-`, `-`) → (`JJ_MAX`, `1100`)
- **KEY5/VAL5**: (`-`, `-`) → (`HH_MIN`, `2000`)
- **KEY6/VAL6**: (`-`, `-`) → (`HH_MAX`, `2400`)

#### ■ NO 54 행 변경 내역
- **GOTO**: `-` → `CHK2`
- **SPEC1/CON1**: (`-`, `-`) → (`EL_ACD2`, `?KS?`)
- **SPEC2/CON2**: (`-`, `-`) → (`EL_AOPEN`, `1SCO`)
- **SPEC3/CON3**: (`-`, `-`) → (`EL_ECDOP`, `MH1`)
- **SPEC4/CON4**: (`-`, `-`) → (`TYPE_450J`, `GLASTL`)
- **SPEC5/CON5**: (`-`, `-`) → (`EL_DPW`, `N`)
- **SPEC6/CON6**: (`-`, `-`) → (`EL_ECJJ`, `>=1200,<=1500`)
- **SPEC7/CON7**: (`-`, `-`) → (`EL_ECHH`, `>=2000,<=2400`)
- **SPEC8/CON8**: (`-`, `-`) → (`EL_BCDGD`, `N`)
- **SPEC9/CON9**: (`-`, `-`) → (`EL_BCDAD`, `,D,AD`)
- **SPEC10/CON10**: (`-`, `-`) → (`EL_BCS`, `AL`)
- **KEY1/VAL1**: (`CHK`, `-`) → (`C_DOOR_CERTI_NO_2`, `AAA13-J001-25001`)
- **KEY2/VAL2**: (`-`, `-`) → (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-25001`)
- **KEY3/VAL3**: (`-`, `-`) → (`JJ_MIN`, `1200`)
- **KEY4/VAL4**: (`-`, `-`) → (`JJ_MAX`, `1500`)
- **KEY5/VAL5**: (`-`, `-`) → (`HH_MIN`, `2000`)
- **KEY6/VAL6**: (`-`, `-`) → (`HH_MAX`, `2400`)

#### ■ NO 55 행 변경 내역
- **GOTO**: `-` → `CHK2`
- **SPEC1/CON1**: (`C_DOOR_CERTI_NO_2`, `N`) → (`EL_ACD2`, `?KS?`)
- **SPEC2/CON2**: (`TYPE_450J`, `?GLASTL?`) → (`EL_AOPEN`, `1SCO`)
- **SPEC3/CON3**: (`-`, `-`) → (`EL_ECDOP`, `P2H`)
- **SPEC4/CON4**: (`-`, `-`) → (`TYPE_450J`, `GLASTL`)
- **SPEC5/CON5**: (`-`, `-`) → (`EL_DPW`, `N`)
- **SPEC6/CON6**: (`-`, `-`) → (`EL_ECJJ`, `>=900,<=1100`)
- **SPEC7/CON7**: (`-`, `-`) → (`EL_ECHH`, `>=2000,<=2400`)
- **SPEC8/CON8**: (`-`, `-`) → (`EL_BCDGD`, `N`)
- **SPEC9/CON9**: (`-`, `-`) → (`EL_BCDAD`, `,N,A`)
- **SPEC10/CON10**: (`-`, `-`) → (`EL_BCS`, `AL`)
- **KEY1/VAL1**: (`CHK`, `- C-DOOR2 부품인증(350J) 없음`) → (`C_DOOR_CERTI_NO_2`, `AAA13-J001-26011`)
- **KEY2/VAL2**: (`CERTI_CMT_E331A`, `{CERTI_CMT_E331A}{CHK}`) → (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-26011`)
- **KEY3/VAL3**: (`-`, `-`) → (`JJ_MIN`, `900`)
- **KEY4/VAL4**: (`-`, `-`) → (`JJ_MAX`, `1100`)
- **KEY5/VAL5**: (`-`, `-`) → (`HH_MIN`, `2000`)
- **KEY6/VAL6**: (`-`, `-`) → (`HH_MAX`, `2400`)

#### ■ NO 56 행 변경 내역
- **GOTO**: `-` → `CHK2`
- **SPEC1/CON1**: (`C_DOOR_CERTI_NO_2`, `N`) → (`EL_ACD2`, `?KS?`)
- **SPEC2/CON2**: (`EL_DPW`, `,N,G`) → (`EL_AOPEN`, `1SCO`)
- **SPEC3/CON3**: (`EL_BCDGD`, `G`) → (`EL_ECDOP`, `P2H`)
- **SPEC4/CON4**: (`-`, `-`) → (`TYPE_450J`, `GLASTL`)
- **SPEC5/CON5**: (`-`, `-`) → (`EL_DPW`, `N`)
- **SPEC6/CON6**: (`-`, `-`) → (`EL_ECJJ`, `>=900,<=1100`)
- **SPEC7/CON7**: (`-`, `-`) → (`EL_ECHH`, `>=2000,<=2400`)
- **SPEC8/CON8**: (`-`, `-`) → (`EL_BCDGD`, `N`)
- **SPEC9/CON9**: (`-`, `-`) → (`EL_BCDAD`, `,D,AD`)
- **SPEC10/CON10**: (`-`, `-`) → (`EL_BCS`, `AL`)
- **KEY1/VAL1**: (`CHK`, `- C-DOOR2 부품인증(350J) 없음`) → (`C_DOOR_CERTI_NO_2`, `AAA13-J001-26012`)
- **KEY2/VAL2**: (`CERTI_CMT_E331A`, `{CERTI_CMT_E331A}{CHK}`) → (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-26012C`)
- **KEY3/VAL3**: (`-`, `-`) → (`JJ_MIN`, `900`)
- **KEY4/VAL4**: (`-`, `-`) → (`JJ_MAX`, `1100`)
- **KEY5/VAL5**: (`-`, `-`) → (`HH_MIN`, `2000`)
- **KEY6/VAL6**: (`-`, `-`) → (`HH_MAX`, `2400`)

#### ■ NO 57 행 변경 내역
- **GOTO**: `-` → `CHK2`
- **SPEC1/CON1**: (`C_DOOR_CERTI_NO_2`, `N`) → (`EL_ACD2`, `?KS?`)
- **SPEC2/CON2**: (`EL_DPW`, `,1,2`) → (`EL_AOPEN`, `1SCO`)
- **SPEC3/CON3**: (`-`, `-`) → (`EL_ECDOP`, `P2H`)
- **SPEC4/CON4**: (`-`, `-`) → (`TYPE_450J`, `GLASTL`)
- **SPEC5/CON5**: (`-`, `-`) → (`EL_DPW`, `N`)
- **SPEC6/CON6**: (`-`, `-`) → (`EL_ECJJ`, `>=1200,<=1500`)
- **SPEC7/CON7**: (`-`, `-`) → (`EL_ECHH`, `>=2000,<=2400`)
- **SPEC8/CON8**: (`-`, `-`) → (`EL_BCDGD`, `N`)
- **SPEC9/CON9**: (`-`, `-`) → (`EL_BCDAD`, `,N,A`)
- **SPEC10/CON10**: (`-`, `-`) → (`EL_BCS`, `AL`)
- **KEY1/VAL1**: (`CHK`, `- C-DOOR2 부품인증(350J) 없음`) → (`C_DOOR_CERTI_NO_2`, `AAA13-J001-26013`)
- **KEY2/VAL2**: (`CERTI_CMT_E331A`, `{CERTI_CMT_E331A}{CHK}`) → (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-26013`)
- **KEY3/VAL3**: (`-`, `-`) → (`JJ_MIN`, `1200`)
- **KEY4/VAL4**: (`-`, `-`) → (`JJ_MAX`, `1500`)
- **KEY5/VAL5**: (`-`, `-`) → (`HH_MIN`, `2000`)
- **KEY6/VAL6**: (`-`, `-`) → (`HH_MAX`, `2400`)

#### ■ NO 58 행 변경 내역
- **GOTO**: `-` → `CHK2`
- **SPEC1/CON1**: (`C_DOOR_CERTI_NO_2`, `!N`) → (`EL_ACD2`, `?KS?`)
- **SPEC2/CON2**: (`EL_ECJJ`, `<{JJ_MIN}`) → (`EL_AOPEN`, `1SCO`)
- **SPEC3/CON3**: (`-`, `-`) → (`EL_ECDOP`, `P2H`)
- **SPEC4/CON4**: (`-`, `-`) → (`TYPE_450J`, `GLASTL`)
- **SPEC5/CON5**: (`-`, `-`) → (`EL_DPW`, `N`)
- **SPEC6/CON6**: (`-`, `-`) → (`EL_ECJJ`, `>=1200,<=1500`)
- **SPEC7/CON7**: (`-`, `-`) → (`EL_ECHH`, `>=2000,<=2400`)
- **SPEC8/CON8**: (`-`, `-`) → (`EL_BCDGD`, `N`)
- **SPEC9/CON9**: (`-`, `-`) → (`EL_BCDAD`, `,D,AD`)
- **SPEC10/CON10**: (`-`, `-`) → (`EL_BCS`, `AL`)
- **KEY1/VAL1**: (`CHK`, `- C-DOOR2 부품인증(350J) JJ 범위 벗어남(현장사양:{EL_ECJJ}mm, 인증범위:{JJ_MIN}~{JJ_MAX}mm) (부품인증번호 : {C_DOOR_CERTI_NO_2_VER})`) → (`C_DOOR_CERTI_NO_2`, `AAA13-J001-26014`)
- **KEY2/VAL2**: (`CERTI_CMT_E331A`, `{CERTI_CMT_E331A}{CHK}`) → (`C_DOOR_CERTI_NO_2_VER`, `AAA13-J001-26014C`)
- **KEY3/VAL3**: (`-`, `-`) → (`JJ_MIN`, `1200`)
- **KEY4/VAL4**: (`-`, `-`) → (`JJ_MAX`, `1500`)
- **KEY5/VAL5**: (`-`, `-`) → (`HH_MIN`, `2000`)
- **KEY6/VAL6**: (`-`, `-`) → (`HH_MAX`, `2400`)

#### ■ NO 59 행 변경 내역
- **ADDR**: `-` → `CHK2`
- **SPEC1/CON1**: (`C_DOOR_CERTI_NO_2`, `!N`) → (`-`, `-`)
- **SPEC2/CON2**: (`EL_ECJJ`, `>{JJ_MAX}`) → (`-`, `-`)
- **KEY1/VAL1**: (`CHK`, `- C-DOOR2 부품인증(350J) JJ 범위 벗어남(현장사양:{EL_ECJJ}mm, 인증범위:{JJ_MIN}~{JJ_MAX}mm) (부품인증번호 : {C_DOOR_CERTI_NO_2_VER})`) → (`-`, `-`)
- **KEY2/VAL2**: (`CERTI_CMT_E331A`, `{CERTI_CMT_E331A}{CHK}`) → (`-`, `-`)

#### ■ NO 60 행 변경 내역
- **SPEC1/CON1**: (`C_DOOR_CERTI_NO_2`, `!N`) → (`-`, `-`)
- **SPEC2/CON2**: (`EL_ECHH`, `<{HH_MIN}`) → (`-`, `-`)
- **KEY1/VAL1**: (`CHK`, `- C-DOOR2 부품인증(350J) HH 범위 벗어남(현장사양:{EL_ECHH}mm, 인증범위:{HH_MIN}~{HH_MAX}mm) (부품인증번호 : {C_DOOR_CERTI_NO_2_VER})`) → (`CHK`, `-`)
- **KEY2/VAL2**: (`CERTI_CMT_E331A`, `{CERTI_CMT_E331A}{CHK}`) → (`-`, `-`)

#### ■ NO 61 행 변경 내역
- **SPEC1/CON1**: (`C_DOOR_CERTI_NO_2`, `!N`) → (`C_DOOR_CERTI_NO_2`, `N`)
- **SPEC2/CON2**: (`EL_ECHH`, `>{HH_MAX}`) → (`TYPE_450J`, `?GLASTL?`)
- **KEY1/VAL1**: (`CHK`, `- C-DOOR2 부품인증(350J) HH 범위 벗어남(현장사양:{EL_ECHH}mm, 인증범위:{HH_MIN}~{HH_MAX}mm) (부품인증번호 : {C_DOOR_CERTI_NO_2_VER})`) → (`CHK`, `- C-DOOR2 부품인증(350J) 없음`)

## 3. 종합 평가 및 조치 요약
1. **인증 사양 보완**: 최신 버전(v13)은 C-DOOR2(1SCO, MH1/P2H, GLASTL 사양)에 대한 신규 부품인증서(`AAA13-J001-*`) 수배 로직이 완성되었습니다.
2. **분기 구조 체계화**: `GOTO CHK2`를 통해 C-DOOR2 인증번호 발급 후 JJ, HH 폭/높이 범위 체킹 구간(`CHK2`, NO 59~67)으로 자동 연동되도록 개선되었습니다.