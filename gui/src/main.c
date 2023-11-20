/*
Copyright (c) 2012, Broadcom Europe Ltd
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the copyright holder nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

// Test app for VG font library.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <unistd.h>

#include "bcm_host.h"
#include "vgfont.h"

int32_t render_subtitle(GRAPHICS_RESOURCE_HANDLE img, const char *text, const uint32_t text_size, const uint32_t text_size_selected, const uint32_t x_offset, const uint32_t y_offset, uint32_t fontcolor)
{
    uint32_t height=0;
    uint32_t img_w, img_h;

    graphics_get_resource_size(img, &img_w, &img_h);

    // split now points to last line of text. split-text = length of initial text. text_length-(split-text) is length of last line
    if (fontcolor == 7) {
    graphics_resource_render_text_ext(img, x_offset, y_offset-height,
                                     GRAPHICS_RESOURCE_WIDTH,
                                     GRAPHICS_RESOURCE_HEIGHT,
                                     GRAPHICS_RGBA32(255,255,255,100), /* fg */
                                     GRAPHICS_RGBA32(20,20,20,200), /* bg */
                                     text, 90, text_size);
        }
    if (fontcolor == 6) {
    graphics_resource_render_text_ext(img, x_offset, y_offset-height,
                                     GRAPHICS_RESOURCE_WIDTH,
                                     GRAPHICS_RESOURCE_HEIGHT,
                                     GRAPHICS_RGBA32(225,255,255,0), /* fg */
                                     GRAPHICS_RGBA32(0,0,0,0), /* bg */
                                     text, 90, text_size);
        }
    if (fontcolor == 5) {
    graphics_resource_render_text_ext(img, x_offset, y_offset-height,
                                     GRAPHICS_RESOURCE_WIDTH,
                                     GRAPHICS_RESOURCE_HEIGHT,
                                     GRAPHICS_RGBA32(255,255,255,0xff), /* fg */
                                     GRAPHICS_RGBA32(0,0,0,150), /* bg */
                                     text, 90, text_size);
        }
    if (fontcolor == 4) {
    graphics_resource_render_text_ext(img, x_offset, y_offset-height,
                                     GRAPHICS_RESOURCE_WIDTH,
                                     GRAPHICS_RESOURCE_HEIGHT,
                                     GRAPHICS_RGBA32(30,255,255,0xff), /* fg */
                                     GRAPHICS_RGBA32(0,0,0,0), /* bg */
                                     text, 90, text_size);
        }
    if (fontcolor == 3) {
    graphics_resource_render_text_ext(img, x_offset, y_offset-height,
                                     GRAPHICS_RESOURCE_WIDTH,
                                     GRAPHICS_RESOURCE_HEIGHT,
                                     GRAPHICS_RGBA32(30,30,255,0xff), /* fg */
                                     GRAPHICS_RGBA32(0,0,0,0), /* bg */
                                     text, 90, text_size);
        }
    if (fontcolor == 2) {
    graphics_resource_render_text_ext(img, x_offset, y_offset-height,
                                     GRAPHICS_RESOURCE_WIDTH,
                                     GRAPHICS_RESOURCE_HEIGHT,
                                     GRAPHICS_RGBA32(30,255,30,0xff), /* fg */
                                     GRAPHICS_RGBA32(0,0,0,0), /* bg */
                                     text, 90, text_size);
        }
    if (fontcolor == 1) {
    graphics_resource_render_text_ext(img, x_offset, y_offset-height,
                                     GRAPHICS_RESOURCE_WIDTH,
                                     GRAPHICS_RESOURCE_HEIGHT,
                                     GRAPHICS_RGBA32(0,0,0,0xff), /* fg */
                                     GRAPHICS_RGBA32(30,255,255,0xff), /* bg */
                                     text, 90, text_size_selected);
        }
    return 0;
    }

int main(void)
{
    GRAPHICS_RESOURCE_HANDLE img;
    uint32_t width, height;
    int LAYER=10;
    bcm_host_init();
    int s;

    s = gx_graphics_init(".");
    assert(s == 0);

    s = graphics_get_display_size(0, &width, &height);
    assert(s == 0);

    s = gx_create_window(0, width, height, GRAPHICS_RESOURCE_RGBA32, &img);
    assert(s == 0);

    // transparent before display to avoid screen flash
    graphics_resource_fill(img, 0, 0, width, height, GRAPHICS_RGBA32(0,0,0,0x00));

    graphics_display_resource(img, 0, LAYER, 0, 0, GRAPHICS_RESOURCE_WIDTH, GRAPHICS_RESOURCE_HEIGHT, VC_DISPMAN_ROT0, 1);

    FILE * fp;
    FILE * fp2;
    FILE * fp3;
    char * line = 0;
    //char * b = NULL;
    size_t len = 0;
    ssize_t read = 0;
    int linenr = 0;
    int selected;
    int showmenu;
    int header;
    int menuadd = 1;
    char newread[500];
    char oldread[500];
    char vumeter[130];
    uint32_t y_offset2 = 0;
    uint32_t y_offset3 = 21;
    uint32_t y_offset4 = 42;
    uint32_t y_offset5 = 421;
    uint32_t y_offset6 = 442; 
    uint32_t y_offset = 466;
    uint32_t text_size = 15;
    uint32_t text_size_selected = 16;
    int space = 10;
    int morespace = 12;
    int rectime = 700;
    int color = 3;
    int row1 = 0;
    int row2 = 0;
    int row3 = 0;
    int row4 = 0;
    int row5 = 0;
    int moverow = 0;
    if (width == 1920){
        y_offset2 = 5;
        y_offset3 = 45;
        y_offset4 = 85;
        y_offset5 = 960;
        y_offset6 = 1000;
        y_offset = 1040;
        rectime = 1600;
        text_size = 30;
        text_size_selected = 32;
        space = 23;
        morespace = 27;
    }
    if (width < 799){
        y_offset2 = 16;
        y_offset3 = 30;
        y_offset4 = 43;
        y_offset5 = 433;
        y_offset6 = 445;
        y_offset = 457;
        rectime = 600;
        text_size = 11;
        text_size_selected = 11;
        space = 7;
        morespace = 10;
        moverow = 20;
    }
    while (1) {
        // char ch;
        linenr = 0;
        fp = fopen("/dev/shm/interface","r");
        if (fp != NULL){
            fread(newread, sizeof(char), 500, fp);
            fclose(fp);
        }
        fp3 = fopen("/dev/shm/vumeter","r");
        while(fgets(vumeter, 130, fp3) != NULL);
        fclose(fp3);
        // check if something has changed
        if (strcmp(newread, oldread) != 0) {
            strcpy(oldread, newread);
            //const char *text = "Never give up on your dreams";
            color = 3;
            row1 = 0+moverow;
            row2 = 0+moverow;
            row3 = 0+moverow;
            row4 = 0+moverow;
            row5 = 0+moverow;
            graphics_resource_fill(img, 0, 0, width, height, GRAPHICS_RGBA32(0,0,0,0x00));
            // blue, at the top (y=40)
            // selected 0 1 2 3 4 5 6 7 8

            // draw the text if updated
            fp2 = fopen("/dev/shm/interface", "r");
            if (fp2 != NULL){
                while ((read = getline(&line, &len, fp2)) != -1) {
                    //line = b;
                    read = read - 1; //don't count the selected line
                    line[read] = '\0'; //remove return char
                    //strcat(line, " ");
                    //printf("%s",line);
                    if (linenr == 0)
                        selected = atoi(line);
                    if (linenr == 1)
                        showmenu = atoi(line);
                    if (linenr == selected + 2 + menuadd)
                        color = 1; //selected color
                    else {
                        if (showmenu == 1)
                            color = 5; //unselected;
                        if (showmenu == 2)
                            color = 7;
                        if (showmenu == 0)
                            color = 6;
                        };
                    if ((linenr == 2) && (read == 0))
                        header = 0;
                    if ((linenr == 2) && (read > 0))
                        header = 1;
                    if (selected == 420){
                        if (linenr == 1)
                            render_subtitle(img, line, text_size, text_size_selected, moverow, y_offset2, 5);
                        if (linenr > 1) {
                            render_subtitle(img, line, text_size, text_size_selected, row1, y_offset3, 5);
                            row1 += read * space + morespace;
                        }
                    }
                    if (header == 0){ //check if normal menu or header menu
                        if (selected < 420){
                            if ((linenr == 6+menuadd) && (read > 0)){ //show recording time if there is any
                                render_subtitle(img, line, text_size, text_size_selected, rectime, y_offset2, 3);
                            }
                            if (linenr >= 2+menuadd && linenr <= 5+menuadd){
                                if (color == 6)
                                    color = 5;
                                render_subtitle(img, line, text_size, text_size_selected, row1, y_offset2, color);
                                row1 += read * space + morespace;
                            }
                            if (linenr >= 7+menuadd && linenr <= 12+menuadd){
                                render_subtitle(img, line, text_size, text_size_selected, row2, y_offset3, color);
                                row2 += read * space + morespace;
                            }
                            if (linenr >= 13+menuadd && linenr <= 20+menuadd){
                                render_subtitle(img, line, text_size, text_size_selected, row3, y_offset4, color);
                                row3 += read * space + morespace;
                            }
                            if (linenr >= 21+menuadd && linenr <= 27+menuadd){
                                render_subtitle(img, line, text_size, text_size_selected, row4, y_offset5, color);
                                row4 += read * space + morespace;
                            }
                            if (linenr >= 28+menuadd && linenr <= 40+menuadd){
                                render_subtitle(img, line, text_size, text_size_selected, row5, y_offset6, color);
                                row5 += read * space + morespace;
                            }
                        }
                    }
                    else { // header menu
                        if (linenr == 1+menuadd)
                            render_subtitle(img, line, text_size, text_size_selected, moverow, y_offset2, 5);
                        if (linenr > 1+menuadd){
                            render_subtitle(img, line, text_size, text_size_selected, row1, y_offset3, color);
                            row1 += read * space + morespace;
                        }
                    }
                    linenr += 1;
                    free(line);
                    line = NULL;
                }
                free(line);
                line = NULL;
                fclose(fp2);
            }
        //graphics_update_displayed_resource(img, 0, 0, 0, 0);
        }
        char s_vol1 = vumeter[85];
        char s_vol2 = vumeter[86];
        char s_vol[1];
        s_vol[0] = s_vol1;
        s_vol[1] = s_vol2;
        int vol = atoi(s_vol);
        int vucolor = 6;
        //printf("%s", s_vol);
        if (vol >= 0 && vol < 35)
            vucolor = 4;
        if (vol >= 35 && vol < 99)
            vucolor = 2;
        if (vol >= 99)
            vucolor = 3;
        render_subtitle(img, vumeter, text_size, text_size_selected , moverow, y_offset, vucolor);
        graphics_update_displayed_resource(img, 0, 0, 0, 0);
        usleep(20000);
    }
    graphics_display_resource(img, 0, LAYER, 0, 0, GRAPHICS_RESOURCE_WIDTH, GRAPHICS_RESOURCE_HEIGHT,  VC_DISPMAN_ROT0, 0);
    graphics_delete_resource(img);
    return 0;
}

