//**********************************************************************************
//  Copyright 2023 Paul Chote, All Rights Reserved
//**********************************************************************************

#include <stdint.h>
#include "gpio.h"

#ifndef ONEWIRE_H
#define ONEWIRE_H

void onewire_measure(const gpin_t* io, char output[20]);

#endif
